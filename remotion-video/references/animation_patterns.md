# Animation Patterns

Reusable animation helpers. Copy and adapt as needed.

## Opacity Patterns

### Fade In

```tsx
function fadeIn(
  frame: number,
  startFrame: number,
  duration: number = 20
): number {
  return interpolate(frame, [startFrame, startFrame + duration], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
}
```

### Fade Out

```tsx
function fadeOut(
  frame: number,
  startFrame: number,
  duration: number = 20
): number {
  return interpolate(frame, [startFrame, startFrame + duration], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
}
```

---

## Position Patterns

### Slide In

```tsx
function slideIn(
  frame: number,
  startFrame: number,
  fps: number,
  direction: 'up' | 'down' | 'left' | 'right' = 'up',
  distance: number = 30
): { opacity: number; x: number; y: number } {
  const progress = spring({
    fps,
    frame: frame - startFrame,
    config: { damping: 200, stiffness: 100 },
  });

  const offset = (1 - progress) * distance;
  const offsets = {
    up: { x: 0, y: offset },
    down: { x: 0, y: -offset },
    left: { x: offset, y: 0 },
    right: { x: -offset, y: 0 },
  };

  return {
    opacity: progress,
    ...offsets[direction],
  };
}

// Usage:
const anim = slideIn(frame, TIMELINE.CARD_ENTER, fps, 'up', 40);
<div style={{
  opacity: anim.opacity,
  transform: `translateY(${anim.y}px)`,
}} />
```

---

## Scale Patterns

### Scale In (Pop)

```tsx
function scaleIn(frame: number, startFrame: number, fps: number): number {
  return spring({
    fps,
    frame: frame - startFrame,
    config: { damping: 12, stiffness: 200 },  // Bouncy
  });
}

// Usage:
const scale = scaleIn(frame, TIMELINE.ICON_APPEAR, fps);
<div style={{ transform: `scale(${scale})` }} />
```

### Pulse (Breathing)

```tsx
function pulse(frame: number, fps: number, intensity: number = 0.03): number {
  const cycle = (frame / fps) * Math.PI * 2;  // Full cycle per second
  return Math.sin(cycle) * intensity;
}

// Usage:
const pulseValue = pulse(frame, fps);
<div style={{ transform: `scale(${1 + pulseValue})` }} />
```

---

## Typed Text Pattern

Simulates typing effect:

```tsx
function typedText(
  frame: number,
  startFrame: number,
  text: string,
  framesPerChar: number = 4,
  fps: number = 30
): string {
  const elapsed = frame - startFrame;
  if (elapsed < 0) return '';
  
  const charsToShow = Math.floor(elapsed / framesPerChar);
  return text.slice(0, Math.min(charsToShow, text.length));
}

// Usage:
const displayText = typedText(frame, TIMELINE.TYPE_START, '250.00', 6, fps);
<Input value={`$${displayText}`} />
```

---

## Cursor Animation Pattern

From the sample code - this pattern works well:

```tsx
interface CursorPoint {
  x: number;
  y: number;
  frame: number;
  click?: boolean;
  visible?: boolean;
}

const cursorPath: CursorPoint[] = [
  { x: 600, y: 350, frame: 0, visible: false },
  { x: 600, y: 350, frame: 15, visible: true },      // Appear
  { x: 960, y: 500, frame: 30 },                     // Move to button
  { x: 960, y: 500, frame: 50, click: true },        // Click
  { x: 960, y: 500, frame: 55, visible: false },     // Hide after click
];

// AnimatedCursor component interpolates between points
```

Key insight: **Hide cursor during system interactions** (biometrics, loading states).

---

## Scene Transition Pattern

Fade between multiple scenes:

```tsx
function getSceneOpacity(
  frame: number,
  enterFrame: number,
  exitFrame: number,
  transitionDuration: number = 20
): number {
  const fadeInEnd = enterFrame + transitionDuration;
  const fadeOutStart = exitFrame - transitionDuration;

  if (frame < enterFrame) return 0;
  if (frame > exitFrame) return 0;

  if (frame < fadeInEnd) {
    return interpolate(frame, [enterFrame, fadeInEnd], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  }

  if (frame > fadeOutStart) {
    return interpolate(frame, [fadeOutStart, exitFrame], [1, 0], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
  }

  return 1;
}

// Usage:
const scene1Opacity = getSceneOpacity(frame, TIMELINE.SCENE1_START, TIMELINE.SCENE1_END);
const scene2Opacity = getSceneOpacity(frame, TIMELINE.SCENE2_START, TIMELINE.SCENE2_END);
```

---

## Spring Configurations

```tsx
const springConfig = {
  // Quick settle, minimal bounce
  stiff: { damping: 200, stiffness: 300 },
  
  // Natural feel, slight overshoot
  default: { damping: 15, stiffness: 170 },
  
  // Bouncy, playful
  bouncy: { damping: 10, stiffness: 200 },
  
  // Slow, dramatic
  slow: { damping: 20, stiffness: 80 },
};

// Usage:
spring({ fps, frame, config: springConfig.bouncy });
```

---

## Combining Transforms

Use `makeTransform` from `@remotion/animation-utils`:

```tsx
import { makeTransform, scale, translateY, rotate } from '@remotion/animation-utils';

const transform = makeTransform([
  scale(scaleValue),
  translateY(yOffset),
  rotate(rotation),
]);

<div style={{ transform }} />
```

See: https://www.remotion.dev/docs/animation-utils/make-transform
