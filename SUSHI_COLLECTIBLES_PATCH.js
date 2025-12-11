// Sushi Collectible class - Different types of sushi!
class Collectible {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 40;
        this.height = 30;
        this.collected = false;
        this.pulseSize = 0;
        this.id = Date.now() + Math.random();
        
        // Random sushi type
        this.sushiType = Math.floor(Math.random() * 5);
        const sushiTypes = [
            {name: 'Nigiri', value: 50, color: '#ff6b6b'},
            {name: 'Maki', value: 75, color: '#4ecdc4'},
            {name: 'Sashimi', value: 100, color: '#ff8c42'},
            {name: 'Temaki', value: 60, color: '#95e1d3'},
            {name: 'Onigiri', value: 40, color: '#f38181'}
        ];
        this.name = sushiTypes[this.sushiType].name;
        this.value = sushiTypes[this.sushiType].value;
        this.color = sushiTypes[this.sushiType].color;
    }

    update() {
        // Pulse animation
        this.pulseSize = Math.sin(Date.now() * 0.005) * 3;
    }

    draw() {
        const pixelSize = 3;
        const size = 3 + this.pulseSize / 3;
        
        // Glow effect
        ctx.shadowBlur = 15;
        ctx.shadowColor = this.color;
        
        // Different sushi patterns
        let sushiPattern;
        switch(this.sushiType) {
            case 0: // Nigiri (rice + fish)
                sushiPattern = [
                    [0,0,2,2,2,2,2,2,0,0],
                    [0,2,2,2,2,2,2,2,2,0],
                    [2,1,1,1,1,1,1,1,1,2],
                    [2,1,1,1,1,1,1,1,1,2],
                    [2,1,1,1,1,1,1,1,1,2],
                    [0,2,2,2,2,2,2,2,2,0]
                ];
                break;
            case 1: // Maki (roll)
                sushiPattern = [
                    [0,0,3,3,3,3,3,3,0,0],
                    [0,3,2,2,2,2,2,2,3,0],
                    [3,2,1,1,1,1,1,1,2,3],
                    [3,2,1,4,4,4,4,1,2,3],
                    [3,2,1,1,1,1,1,1,2,3],
                    [0,3,2,2,2,2,2,2,3,0],
                    [0,0,3,3,3,3,3,3,0,0]
                ];
                break;
            case 2: // Sashimi (just fish)
                sushiPattern = [
                    [0,0,2,2,2,2,2,0,0,0],
                    [0,2,2,2,2,2,2,2,0,0],
                    [2,2,2,2,2,2,2,2,2,0],
                    [2,2,2,2,2,2,2,2,2,2],
                    [0,2,2,2,2,2,2,2,2,0],
                    [0,0,2,2,2,2,2,2,0,0]
                ];
                break;
            case 3: // Temaki (cone)
                sushiPattern = [
                    [0,0,0,0,3,3,3,3,3,3],
                    [0,0,0,3,2,2,2,2,2,3],
                    [0,0,3,2,1,1,1,1,2,3],
                    [0,3,2,1,1,4,4,1,2,0],
                    [3,2,1,1,1,1,1,2,0,0],
                    [3,2,2,2,2,2,2,0,0,0],
                    [3,3,3,3,3,3,0,0,0,0]
                ];
                break;
            case 4: // Onigiri (rice ball)
                sushiPattern = [
                    [0,0,1,1,1,1,1,1,0,0],
                    [0,1,1,1,1,1,1,1,1,0],
                    [1,1,1,1,1,1,1,1,1,1],
                    [1,1,1,3,3,3,3,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1],
                    [0,1,1,1,1,1,1,1,1,0],
                    [0,0,1,1,1,1,1,1,0,0]
                ];
                break;
        }
        
        // Draw sushi pixel by pixel
        for (let row = 0; row < sushiPattern.length; row++) {
            for (let col = 0; col < sushiPattern[row].length; col++) {
                const pixel = sushiPattern[row][col];
                if (pixel === 0) continue;
                
                let color;
                if (pixel === 1) color = '#ffffff';      // White rice
                else if (pixel === 2) color = this.color; // Fish/filling
                else if (pixel === 3) color = '#2d5016';  // Nori (seaweed)
                else if (pixel === 4) color = '#ff6b6b';  // Red filling
                
                ctx.fillStyle = color;
                ctx.fillRect(
                    this.x + col * size,
                    this.y + row * size,
                    size,
                    size
                );
            }
        }
        
        ctx.shadowBlur = 0;
        
        // Draw sushi name and value
        ctx.fillStyle = this.color;
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(this.name, this.x + this.width/2, this.y - 15);
        
        ctx.fillStyle = '#ffff00';
        ctx.font = 'bold 12px Arial';
        ctx.fillText(`+${this.value}`, this.x + this.width/2, this.y - 3);
    }

    collidesWith(player) {
        return player.x < this.x + this.width &&
               player.x + player.width > this.x &&
               player.y < this.y + this.height &&
               player.y + player.height > this.y;
    }
}

// Random sushi spawner - spawns every 3-5 seconds
function spawnRandomSushi() {
    const x = Math.random() * (canvas.width - 50);
    const y = Math.random() * (canvas.height - 100);
    const sushi = new Collectible(x, y);
    game.collectibles.push(sushi);
    console.log(`🍣 ${sushi.name} spawned! Value: +${sushi.value}`);
}

// Start auto-spawning sushi
setInterval(() => {
    if (!game.gameOver && game.collectibles.length < 5) {
        spawnRandomSushi();
    }
}, 3000 + Math.random() * 2000);  // Every 3-5 seconds
