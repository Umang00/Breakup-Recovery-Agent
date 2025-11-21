# Music API Implementation Notes

This document contains notes for future reference if we decide to re-implement external music API integration.

## Why We Chose Curated List Over API

### Last.fm API Testing Results

We tested the Last.fm API integration but encountered issues:

1. **Non-English Songs**: API returned German, French, Korean songs that weren't universally relatable
2. **Tag Quality Issues**: User-generated tags like "empowerment" and "healing" had inconsistent results
3. **Obscure Artists**: Some results were too niche (e.g., "sign 0" by Chouchou)
4. **Inconsistent Relevance**: Even with 100k+ playcount filter, song themes didn't always match

### Decision

Use a curated database of 105 verified therapeutic songs with random selection for:
- Consistent quality
- Universal relatability
- "Infinite playlist" feel (different songs each session)
- No external API dependency
- Faster response times

---

## If Re-implementing Last.fm API

### Setup

1. **Get API Key**: https://www.last.fm/api/account/create (free, read-only)
2. **Library**: `pylast==5.3.0`
3. **Install**: `pip install pylast`

### Best Practices

```python
import pylast

# Initialize
network = pylast.LastFMNetwork(api_key="YOUR_API_KEY")

# Best tags for breakup recovery
TAGS = {
    "release": ["heartbreak", "sad", "breakup", "melancholy"],
    "empowerment": ["empowerment", "confident", "girl power", "anthems"],
    "healing": ["healing", "hopeful", "uplifting", "inspirational"]
}

# Get songs by tag
tag = network.get_tag("heartbreak")
top_tracks = tag.get_top_tracks(limit=20)

# Filter by popularity (100k+ plays recommended)
MIN_PLAYCOUNT = 100000
for track in top_tracks:
    playcount = track.item.get_playcount()
    if playcount >= MIN_PLAYCOUNT:
        print(f"{track.item.title} by {track.item.artist.name}")
```

### Key Endpoints

| Endpoint | Use Case |
|----------|----------|
| `tag.getTopTracks` | Get songs by emotional tag |
| `track.search` | Search for specific songs |
| `track.getSimilar` | Find similar songs |
| `artist.getTopTracks` | Get top songs from therapeutic artists |

### Rate Limits

- 5 requests/second (averaged over 5 minutes)
- Free for non-commercial use
- Contact partners@last.fm for higher limits

### Deduplication Strategy

When combining API results with curated list:

```python
def normalize_key(title, artist):
    return f"{title.lower().strip()}|{artist.lower().strip()}"

# Pre-load curated song keys
curated_keys = {normalize_key(s['title'], s['artist']) for s in CURATED_SONGS}

# Skip API songs that match curated
for api_song in api_results:
    if normalize_key(api_song.title, api_song.artist) not in curated_keys:
        # Add to results
```

---

## Current Implementation

Music recommendations are now handled directly in `ai_breakup_recovery_agent.py`:

- **105 curated songs** (35 per category)
- **Random selection**: 5 songs per category per session
- **Categories**: Emotional Release, Empowerment, Hope & Healing
- **Artists include**: Olivia Rodrigo, Taylor Swift, Adele, SZA, BTS, Billie Eilish, etc.

---

*Last updated: November 2024*
