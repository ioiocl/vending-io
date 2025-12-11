use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

declare_id!("E8v2TkXVJEbB7VKCMAVvJ1y2ULTrdqZ223guSpdtWtHf");

#[program]
pub mod ioio_game {
    use super::*;

    /// Initialize the game program
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let leaderboard = &mut ctx.accounts.leaderboard;
        leaderboard.authority = ctx.accounts.authority.key();
        leaderboard.total_games = 0;
        leaderboard.entries = Vec::new();
        Ok(())
    }

    /// Start a new game session (called when user pays)
    pub fn start_game_session(
        ctx: Context<StartGameSession>,
        amount: u64,
    ) -> Result<()> {
        let game_session = &mut ctx.accounts.game_session;
        let clock = Clock::get()?;

        game_session.player = ctx.accounts.player.key();
        game_session.amount_paid = amount;
        game_session.timestamp = clock.unix_timestamp;
        game_session.game_started = false;
        game_session.score = 0;
        game_session.completed = false;
        game_session.bump = ctx.bumps.game_session;

        // Transfer IOIO tokens from player to game vault
        let cpi_accounts = Transfer {
            from: ctx.accounts.player_token_account.to_account_info(),
            to: ctx.accounts.game_vault.to_account_info(),
            authority: ctx.accounts.player.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        token::transfer(cpi_ctx, amount)?;

        msg!("Game session started for player: {}", ctx.accounts.player.key());
        msg!("Amount paid: {} IOIO tokens", amount);

        Ok(())
    }

    /// Activate the game (called when physical button is pressed)
    pub fn activate_game(ctx: Context<ActivateGame>) -> Result<()> {
        let game_session = &mut ctx.accounts.game_session;
        
        require!(!game_session.game_started, ErrorCode::AlreadyStarted);
        require!(!game_session.completed, ErrorCode::GameCompleted);

        game_session.game_started = true;
        
        msg!("Game activated for player: {}", game_session.player);

        Ok(())
    }

    /// Submit final score (called when game ends)
    pub fn submit_score(
        ctx: Context<SubmitScore>,
        score: u64,
    ) -> Result<()> {
        let game_session = &mut ctx.accounts.game_session;
        let leaderboard = &mut ctx.accounts.leaderboard;
        let clock = Clock::get()?;

        require!(game_session.game_started, ErrorCode::GameNotStarted);
        require!(!game_session.completed, ErrorCode::GameCompleted);

        game_session.score = score;
        game_session.completed = true;

        // Add to leaderboard
        let entry = LeaderboardEntry {
            player: game_session.player,
            score,
            timestamp: clock.unix_timestamp,
        };

        leaderboard.entries.push(entry);
        leaderboard.total_games += 1;

        // Sort leaderboard by score (descending)
        leaderboard.entries.sort_by(|a, b| b.score.cmp(&a.score));

        // Keep only top 100 entries
        if leaderboard.entries.len() > 100 {
            leaderboard.entries.truncate(100);
        }

        msg!("Score submitted: {} for player: {}", score, game_session.player);

        Ok(())
    }

    /// Get leaderboard (view function)
    pub fn get_leaderboard(ctx: Context<GetLeaderboard>) -> Result<()> {
        let leaderboard = &ctx.accounts.leaderboard;
        
        msg!("Total games: {}", leaderboard.total_games);
        msg!("Top scores:");
        
        for (i, entry) in leaderboard.entries.iter().take(10).enumerate() {
            msg!("{}. Player: {} - Score: {}", i + 1, entry.player, entry.score);
        }

        Ok(())
    }
}

// Account structures
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Leaderboard::INIT_SPACE,
        seeds = [b"leaderboard"],
        bump
    )]
    pub leaderboard: Account<'info, Leaderboard>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct StartGameSession<'info> {
    #[account(
        init,
        payer = player,
        space = 8 + GameSession::INIT_SPACE,
        seeds = [b"game_session", player.key().as_ref(), &Clock::get()?.unix_timestamp.to_le_bytes()],
        bump
    )]
    pub game_session: Account<'info, GameSession>,
    
    #[account(mut)]
    pub player: Signer<'info>,
    
    #[account(mut)]
    pub player_token_account: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub game_vault: Account<'info, TokenAccount>,
    
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ActivateGame<'info> {
    #[account(
        mut,
        seeds = [b"game_session", game_session.player.as_ref(), &game_session.timestamp.to_le_bytes()],
        bump = game_session.bump
    )]
    pub game_session: Account<'info, GameSession>,
}

#[derive(Accounts)]
pub struct SubmitScore<'info> {
    #[account(
        mut,
        seeds = [b"game_session", game_session.player.as_ref(), &game_session.timestamp.to_le_bytes()],
        bump = game_session.bump
    )]
    pub game_session: Account<'info, GameSession>,
    
    #[account(
        mut,
        seeds = [b"leaderboard"],
        bump
    )]
    pub leaderboard: Account<'info, Leaderboard>,
}

#[derive(Accounts)]
pub struct GetLeaderboard<'info> {
    #[account(
        seeds = [b"leaderboard"],
        bump
    )]
    pub leaderboard: Account<'info, Leaderboard>,
}

// Data structures
#[account]
#[derive(InitSpace)]
pub struct GameSession {
    pub player: Pubkey,           // 32 bytes
    pub amount_paid: u64,          // 8 bytes
    pub timestamp: i64,            // 8 bytes
    pub game_started: bool,        // 1 byte
    pub score: u64,                // 8 bytes
    pub completed: bool,           // 1 byte
    pub bump: u8,                  // 1 byte
}

#[account]
#[derive(InitSpace)]
pub struct Leaderboard {
    pub authority: Pubkey,         // 32 bytes
    pub total_games: u64,          // 8 bytes
    #[max_len(100)]
    pub entries: Vec<LeaderboardEntry>, // 100 entries max
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct LeaderboardEntry {
    pub player: Pubkey,            // 32 bytes
    pub score: u64,                // 8 bytes
    pub timestamp: i64,            // 8 bytes
}

// Error codes
#[error_code]
pub enum ErrorCode {
    #[msg("Game has already been started")]
    AlreadyStarted,
    
    #[msg("Game has not been started yet")]
    GameNotStarted,
    
    #[msg("Game has already been completed")]
    GameCompleted,
}
