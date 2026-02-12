// countryConfig.ts

// Country-specific TikTok content styles and hashtag configurations

const countryConfig = {
    USA: {
        styles: {
            videos: [
                { style: 'trendy', hashtags: ['#trendy', '#viral'] },
                { style: 'funny', hashtags: ['#comedy', '#funnymoments'] }
            ]
        }
    },
    UK: {
        styles: {
            videos: [
                { style: 'lifestyle', hashtags: ['#lifestyle', '#dailyvibes'] },
                { style: 'educational', hashtags: ['#learnontiktok', '#didyouknow'] }
            ]
        }
    },
    India: {
        styles: {
            videos: [
                { style: 'cultural', hashtags: ['#indianculture', '#desitiktok'] },
                { style: 'dance', hashtags: ['#dancechallenge', '#tiktokdance'] }
            ]
        }
    }
};

export default countryConfig;
