# persona-audio-toybox

## Clip metadata SSOT

Clip metadata is fixed at:

- `assets/<project>/clips/clip_meta.json`
- key: clip basename (example `CUT001.mp4`)

```json
{
  "CUT001.mp4": {
    "group_id": "g_intro",
    "tags": ["wide", "establishing"],
    "source": "oiiooi",
    "notes": ""
  }
}
```

## Reorder distance definition

Distance is defined as absolute cut index difference.

- Same `basename`: distance 1 is prohibited (existing rule)
- Same `group_id`: high penalty when distance <= 2
- Same `tag`: small penalty when distance 1

## Report metric definitions

- `TAG_COVERAGE = cuts_with_at_least_1_tag / CUT_COUNT`
- `GROUP_COVERAGE = cuts_with_group_id / CUT_COUNT`
- `GROUP_NEAR_VIOLATIONS = pair_count_with_same_group_id_and_distance<=2`
