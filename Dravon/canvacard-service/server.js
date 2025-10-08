const express = require('express');
const cors = require('cors');
const { Rank } = require('canvacard');

const app = express();
const PORT = 3007;

app.use(cors());
app.use(express.json({ limit: '10mb' }));

app.post('/generate-rank-card', async (req, res) => {
    try {
        const { 
            username, 
            discriminator, 
            avatar, 
            level, 
            rank, 
            currentXP, 
            requiredXP,
            status = 'online',
            background = null
        } = req.body;

        console.log('Generating card for:', username, 'Level:', level, 'XP:', currentXP);

        const card = new Rank()
            .setAvatar(avatar)
            .setCurrentXP(currentXP)
            .setRequiredXP(requiredXP)
            .setLevel(level)
            .setRank(rank)
            .setProgressBar('#23d160', 'COLOR')
            .setUsername(username)
            .setDiscriminator(discriminator || '0000')
            .setStatus(status);

        if (background) {
            card.setBackground('IMAGE', background);
        }

        const buffer = await card.build();
        
        res.set({
            'Content-Type': 'image/png',
            'Content-Length': buffer.length
        });
        
        res.send(buffer);
    } catch (error) {
        console.error('Error generating rank card:', error);
        res.status(500).json({ error: 'Failed to generate rank card', details: error.message, stack: error.stack });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'OK', service: 'Canvacard', version: '6.0.5' });
});

app.listen(PORT, () => {
    console.log(`✅ Canvacard service running on port ${PORT}`);
});