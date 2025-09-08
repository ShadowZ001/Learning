const axios = require('axios');

async function testLogin() {
    try {
        console.log('Testing login API...');
        
        const response = await axios.post('http://localhost:3000/api/login', {
            username: 'shadow',
            password: 'shadow06'
        }, {
            headers: { 'Content-Type': 'application/json' }
        });
        
        console.log('✅ Login successful:', response.data);
    } catch (error) {
        console.log('❌ Login failed:', error.response?.data || error.message);
    }
}

testLogin();