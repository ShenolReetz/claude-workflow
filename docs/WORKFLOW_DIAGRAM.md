# Automated Video Creation Workflow Diagram

![Workflow Diagram](diagrams/workflow-diagram.png)

## Workflow Description

### Overview
This workflow automates the creation of "Top 5 Product" countdown videos by scraping Amazon product data, generating multimedia content, and distributing across multiple social media platforms.

### Trigger Schedule
- **Frequency**: 3 times daily
- **Times**: 09:00, 13:00, and 15:00

### Detailed Process Flow

1. **Initial Trigger & Title Selection**
   - Source: Airtable database with 1000+ product category titles
   - Selects next "Pending" title from queue

2. **Amazon Product Research**
   - Scrapes Amazon for top products
   - Ranks by reviews and ratings
   - Saves product data, images, and affiliate links

3. **Keyword Generation**
   - Creates platform-specific keywords
   - YouTube, Instagram, TikTok, WordPress

4. **Content Creation**
   - Generates video title and descriptions
   - Creates scripts for intro, products, and outro

5. **Audio Generation**
   - Text-to-speech for all content
   - Saves to Google Drive

6. **Video Creation**
   - Assembles all media into countdown video
   - Uploads to Google Drive

7. **Social Media Distribution**
   - Posts to YouTube, Instagram, TikTok
   - Creates WordPress blog post

8. **Status Update**
   - Marks title as "Done" in Airtable
