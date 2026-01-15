# Remotion Core Reference

## Official Remotion LLM Prompt

The following is the official Remotion system prompt for LLMs, also hosted at https://www.remotion.dev/llms.txt

---

Remotion is a framework that creates videos programmatically using React.js and TypeScript.

### Project Structure

```
src/
├── index.ts      # Entry file with registerRoot()
├── Root.tsx      # Compositions defined here
└── MyComp.tsx    # Video components
```

### Composition Definition

```tsx
<Composition
  id="MyComp"
  component={MyComp}
  durationInFrames={120}
  width={1920}
  height={1080}
  fps={30}
  defaultProps={{}}
/>
```

Default: 1920×1080, 30fps.

### Essential Hooks

```tsx
const frame = useCurrentFrame();  // Current frame number (starts at 0)
const { fps, durationInFrames, width, height } = useVideoConfig();
```

### Core Components

**AbsoluteFill** - Layer elements on top of each other:
```tsx
<AbsoluteFill>
  <AbsoluteFill style={{background: 'blue'}}>Back</AbsoluteFill>
  <AbsoluteFill>Front</AbsoluteFill>
</AbsoluteFill>
```

**Sequence** - Offset elements in time:
```tsx
<Sequence from={10} durationInFrames={20}>
  <div>Appears at frame 10, useCurrentFrame() starts at 0</div>
</Sequence>
```

**Series** - Sequential elements:
```tsx
<Series>
  <Series.Sequence durationInFrames={20}><A /></Series.Sequence>
  <Series.Sequence durationInFrames={30}><B /></Series.Sequence>
</Series>
```

**TransitionSeries** - With transitions:
```tsx
<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={60}><A /></TransitionSeries.Sequence>
  <TransitionSeries.Transition timing={springTiming({...})} presentation={fade()} />
  <TransitionSeries.Sequence durationInFrames={60}><B /></TransitionSeries.Sequence>
</TransitionSeries>
```

### Media Components

```tsx
import { Video, Audio } from '@remotion/media';
import { Img, staticFile } from 'remotion';
import { Gif } from '@remotion/gif';

<Video src="url" volume={0.5} trimBefore={10} trimAfter={100} />
<Audio src={staticFile('audio.mp3')} volume={1} />
<Img src={staticFile('image.png')} />
<Gif src="url" />
```

### interpolate()

Map frame ranges to value ranges:

```tsx
const opacity = interpolate(frame, [0, 60], [0, 1], {
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});
```

**Always use clamp** to prevent values overshooting.

### spring()

Natural bounce animations:

```tsx
const scale = spring({
  fps,
  frame,
  config: { damping: 200 },  // Higher = less bounce
});
```

### Randomness

Use deterministic `random()`, never `Math.random()`:

```tsx
import { random } from 'remotion';
const value = random('my-seed');  // 0-1, same every render
```

### Rendering

```bash
npx remotion render MyComp           # Render video
npx remotion still MyComp            # Render single frame
```

---

## Timing-Specific Guidance

### Connecting Storyboard to Code

| Storyboard Element | Code Pattern |
|-------------------|--------------|
| `<event frame="60">` | `TIMELINE.EVENT_NAME: 60` |
| `<frame_range>60-239</frame_range>` | `interpolate(frame, [60, 239], [0, 1])` |
| Scene start | `Sequence from={TIMELINE.SCENE_START}` |
| Spring at event | `spring({ frame: frame - TIMELINE.EVENT, fps })` |

### Common Timing Mistakes

| Mistake | Code Smell | Fix |
|---------|------------|-----|
| Hardcoded magic numbers | `[0, 40]` with no comment | Use TIMELINE constants |
| Missing extrapolate clamp | Values go past 1 or below 0 | Always add `extrapolateLeft/Right: 'clamp'` |
| Spring without offset | Animation starts at frame 0 | `spring({ frame: frame - TIMELINE.START, ... })` |
| Scene logic scattered | Multiple `if (frame > X)` checks | Use `getPhase(frame)` helper |

### Phase Helper Pattern

```tsx
function getPhase(frame: number): string {
  if (frame < TIMELINE.SCENE_2) return 'scene-1';
  if (frame < TIMELINE.SCENE_3) return 'scene-2';
  return 'scene-3';
}
```

### Scene Opacity Pattern

```tsx
function getSceneOpacity(
  frame: number,
  enterFrame: number,
  exitFrame: number,
  fadeDuration: number = 20
): number {
  if (frame < enterFrame || frame > exitFrame) return 0;
  
  const fadeIn = interpolate(
    frame, [enterFrame, enterFrame + fadeDuration], [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  const fadeOut = interpolate(
    frame, [exitFrame - fadeDuration, exitFrame], [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  
  return Math.min(fadeIn, fadeOut);
}
```

---

## Links for Advanced Patterns

- **interpolate**: https://www.remotion.dev/docs/interpolate
- **spring**: https://www.remotion.dev/docs/spring
- **Sequence**: https://www.remotion.dev/docs/sequence
- **Series**: https://www.remotion.dev/docs/series
- **TransitionSeries**: https://www.remotion.dev/docs/transitions
- **useCurrentFrame**: https://www.remotion.dev/docs/use-current-frame
- **useVideoConfig**: https://www.remotion.dev/docs/use-video-config
- **Flickering issues**: https://www.remotion.dev/docs/flickering (IMPORTANT - understand render model)
- **Audio**: https://www.remotion.dev/docs/using-audio
- **makeTransform**: https://www.remotion.dev/docs/animation-utils/make-transform
