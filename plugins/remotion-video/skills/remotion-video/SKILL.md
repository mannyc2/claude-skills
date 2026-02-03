---
name: remotion-video
description: Create well-paced, narrative-driven videos using Remotion. Use when asked to create videos, animations, or motion graphics with Remotion, or when working on existing Remotion projects. Triggers on requests like "create a video", "make an animation", "Remotion project", "product demo video", "landing page video", "explainer video", or any programmatic video generation task.
---

# Remotion Video Skill

Create videos with proper pacing and narrative structure using Remotion.

## Critical Rule

**NEVER write Remotion code without first producing a Script and Storyboard.**

The #1 failure mode is jumping straight to TIMELINE constants and frame numbers. This produces videos where key moments are rushed and pacing feels off.

## Workflow

Video creation follows four mandatory phases:

1. **SCRIPT** → Define narrative, viewer takeaways, timing intent
2. **STORYBOARD** → Convert to concrete frames, validate pacing
3. **IMPLEMENTATION** → Write Remotion code from storyboard
4. **VALIDATION** → Verify code matches storyboard timings

Do not proceed to phase N+1 until user has reviewed phase N.

---

## Phase 1: Script

The script defines WHAT the video communicates and WHY each scene exists.

### Script Format

```xml
<video_script>
  <metadata>
    <title>[Video title]</title>
    <purpose>[Why this video exists - what it demonstrates]</purpose>
    <target_duration_seconds>[Total length]</target_duration_seconds>
    <fps>30</fps>
    <viewer_takeaway>
      "[One sentence the viewer should think after watching]"
    </viewer_takeaway>
  </metadata>

  <scenes>
    <scene id="1">
      <name>[Scene name]</name>
      <narrative>
        [What this scene communicates. Not just "what's on screen" but 
        what the VIEWER should understand. Include emotional context.]
      </narrative>
      <viewer_should_notice>
        - [Key element 1]
        - [Key element 2]
        - [What's notably ABSENT, if relevant]
      </viewer_should_notice>
      <timing_intent>[brief|standard|emphasis|hero]</timing_intent>
      <timing_rationale>
        [WHY this duration. What does viewer need to read/notice/understand?
        Bad: "Shows the button"
        Good: "User reads headline (1s) + scans 3 features (2s) = 3s minimum"]
      </timing_rationale>
      <minimum_duration_seconds>[For hero moments only]</minimum_duration_seconds>
    </scene>
  </scenes>

  <transitions>
    <transition from="1" to="2">
      <type>[action|crossfade|cut]</type>
      <trigger>[What causes transition]</trigger>
      <transition_duration_frames>[15-30 typical]</transition_duration_frames>
    </transition>
  </transitions>
</video_script>
```

### Timing Intent Vocabulary

| Intent | Duration | Use When |
|--------|----------|----------|
| brief | 1-2s | Context establishment, simple visuals |
| standard | 2-4s | Normal content, single concept to grasp |
| emphasis | 4-6s | Important moment, needs comprehension time |
| hero | 6-10s | Key differentiator, the "money shot" |

### Timing Rationale Requirement

Every scene MUST justify its duration by answering: "What does the viewer need to read, notice, or understand here?"

See `examples/good_script.xml` and `examples/bad_script.xml` for annotated examples.

---

## Phase 2: Storyboard

The storyboard converts timing intents to concrete frame numbers.

### Storyboard Format

```xml
<storyboard fps="30" total_frames="360">
  <timing_validation>
    <total_duration_seconds>12</total_duration_seconds>
    <scenes_breakdown>
      <scene id="1" duration="2s" frames="0-59" />
      <scene id="2" duration="6s" frames="60-239" />
      <scene id="3" duration="4s" frames="240-359" />
    </scenes_breakdown>
    <pacing_check>
      Hero moments get ≥40% of total time? [YES/NO]
      Any scene under minimum duration? [YES/NO - list if yes]
    </pacing_check>
  </timing_validation>

  <frame_by_frame>
    <segment scene="1" name="[Name]">
      <frame_range>0-59</frame_range>
      <events>
        <event frame="0" type="enter">[Description]</event>
        <event frame="30" type="action">[Description]</event>
        <event frame="55" type="exit">[Description]</event>
      </events>
      <cursor_visible>[true/false]</cursor_visible>
    </segment>
  </frame_by_frame>

  <text_on_screen_audit>
    <text scene="1" content="[Text]" frames_visible="50" 
          read_time_needed="1.5s" status="[OK/TOO_SHORT]" />
  </text_on_screen_audit>
</storyboard>
```

### Pacing Validation Checklist

Before proceeding to implementation:

- [ ] Hero moments get ≥40% of total video time
- [ ] No scene under its minimum_duration_seconds
- [ ] All text has adequate read time (3 words/second rule)
- [ ] Transitions don't eat into scene dwell time
- [ ] Cursor hidden during system interactions (biometrics, loading)

---

## Phase 3: Implementation

Convert storyboard to Remotion code.

### Before Writing Code

Read these references:
- `references/remotion_core.md` - Essential API patterns
- `references/animation_patterns.md` - Reusable animation code
- `references/timing_heuristics.md` - Frame math and readability rules

### TIMELINE from Storyboard

Every TIMELINE constant must trace to a storyboard event:

```typescript
// FROM STORYBOARD:
// <segment scene="2" name="Passkey Creation">
//   <frame_range>60-239</frame_range>
//   <events>
//     <event frame="60" type="enter">Biometric dialog fades in</event>
//     <event frame="90" type="state_change">State: "scanning"</event>
//     <event frame="180" type="state_change">State: "success"</event>

const TIMELINE = {
  // Scene 2: Passkey Creation (hero moment - 6s)
  BIOMETRIC_SHOW: 60,
  BIOMETRIC_SCAN: 90,
  BIOMETRIC_SUCCESS: 180,
  BIOMETRIC_EXIT: 230,
};
```

### Using Existing Site Styles

When user has existing global.css and components:

1. Import CSS: `import '../path/to/global.css'`
2. Reuse components directly
3. Watch for conflicts:
   - CSS `transition` properties conflict with frame-based rendering
   - Convert any CSS animations to `interpolate()` calls
   - Hooks assuming browser context may fail during render

---

## Phase 4: Validation

After implementation, verify code matches storyboard:

- [ ] Every storyboard `<event>` has corresponding TIMELINE constant
- [ ] Frame ranges match (no drift from plan)
- [ ] Hero moments weren't compressed
- [ ] Text durations match text_on_screen_audit

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| No script phase | Arbitrary frame numbers | Always write script first |
| Hero moment marked "standard" | Key feature rushes by | Use timing_intent="hero" with minimum 5s |
| Text unreadable | Appears/disappears too fast | Audit: word_count ÷ 3 = seconds needed |
| Cursor during biometrics | Looks like user interaction | cursor_visible=false for system prompts |
| Success state rushed | Feels like glitch | Hold success states 1.5-2s minimum |
| No timing_rationale | Can't justify duration choices | Force reasoning before frame numbers |

---

## Reference Files

- `references/remotion_core.md` - API patterns, official Remotion prompt, links
- `references/animation_patterns.md` - Reusable fade/slide/scale code
- `references/timing_heuristics.md` - Frame math, readability rules, duration guidelines
- `examples/good_script.xml` - Properly paced video script
- `examples/bad_script.xml` - Common mistakes annotated
