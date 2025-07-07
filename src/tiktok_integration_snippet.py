# This code goes after YouTube section (around line 311)

            # Upload to TikTok if enabled
            if self.config.get('tiktok_enabled', False) and video_result.get('video_url'):
                print("\n🎵 Uploading to TikTok...")
                try:
                    from mcp.tiktok_mcp import run_tiktok_upload
                    
                    tiktok_result = await run_tiktok_upload(
                        self.config,
                        video_result['video_url'],
                        pending_title
                    )
                    
                    if tiktok_result.get('success'):
                        print(f"✅ TikTok upload successful!")
                        print(f"   Status: {tiktok_result.get('status', 'PROCESSING')}")
                        
                        # Build caption for storage (useful for tracking)
                        caption = f"{pending_title.get('VideoTitle', '')}\n\n"
                        caption += "Which one would you choose? 🤔\n\n"
                        
                        for i in range(1, 6):
                            product = pending_title.get(f'ProductNo{i}Title', '')
                            if product:
                                caption += f"{i}️⃣ {product}\n"
                        
                        caption += "\n🔗 Links in bio!\n\n"
                        
                        # Extract hashtags
                        keywords = pending_title.get('Keywords', '').split(',')
                        niche_tags = ' '.join([f"#{k.strip().replace(' ', '')}" for k in keywords[:5]])
                        viral_tags = "#amazonfinds #tiktokmademebuyit #musthave #viral #fyp #2025"
                        all_hashtags = f"{viral_tags} {niche_tags}"
                        
                        caption += all_hashtags
                        
                        # Update Airtable with TikTok info
                        tiktok_updates = {
                            'TikTokURL': tiktok_result.get('url', ''),
                            'TikTokVideoID': tiktok_result.get('video_id', ''),
                            'TikTokPublishID': tiktok_result.get('publish_id', ''),
                            'TikTokStatus': tiktok_result.get('status', 'PROCESSING'),
                            'TikTokCaption': caption[:2000],  # Airtable long text limit
                            'TikTokHashtags': all_hashtags,
                            'TikTokUsername': self.config.get('tiktok_username', '@yourusername')
                        }
                        
                        await self.airtable_server.update_record(
                            pending_title['record_id'], 
                            tiktok_updates
                        )
                        print("✅ Updated Airtable with TikTok info")
                        
                    else:
                        print(f"⚠️ TikTok upload failed: {tiktok_result.get('error', 'Unknown error')}")
                        # Don't fail workflow, just log the error
                        
                except Exception as e:
                    print(f"❌ TikTok error: {e}")
                    # Continue workflow even if TikTok fails
                    import traceback
                    traceback.print_exc()
