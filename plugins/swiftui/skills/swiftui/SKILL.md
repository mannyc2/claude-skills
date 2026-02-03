---
name: swiftui
description: Expert guidance for SwiftUI development on Apple platforms. Use when building SwiftUI views, handling state management, working with async/await in views, implementing navigation, debugging performance issues, or adopting new design systems like Liquid Glass. Covers macOS, iOS, watchOS, and visionOS patterns.
---

# SwiftUI Development

## Architecture Patterns

### View Composition

Keep views small and focused. Extract subviews when a view exceeds ~50 lines or has distinct responsibilities:

```swift
// Prefer
struct ProfileView: View {
    var body: some View {
        VStack {
            ProfileHeader(user: user)
            ProfileStats(stats: user.stats)
            ProfileActions(onEdit: editProfile)
        }
    }
}

// Avoid: monolithic views with all logic inline
```

### State Management

Choose the right property wrapper:

| Wrapper | Use Case |
|---------|----------|
| `@State` | View-local values OR owned Observable objects |
| `@Binding` | Two-way connection to parent's state |
| `@Bindable` | Get bindings from Observable objects |
| `@Environment` | Dependency injection, shared services |
| `@AppStorage` | UserDefaults-backed persistence |

**Migration from ObservableObject:**

| Old | New |
|-----|-----|
| `@StateObject` | `@State` |
| `@ObservedObject` | no wrapper (just `var`) or `@Bindable` |
| `@EnvironmentObject` | `@Environment` |
| `ObservableObject` | `@Observable` |
| `@Published` | (not needed) |

**Observable pattern** (preferred over ObservableObject):

```swift
@Observable
class ViewModel {
    var items: [Item] = []
    var isLoading = false
}

struct ContentView: View {
    @State private var viewModel = ViewModel()
    // View automatically tracks accessed properties
}
```

**@Bindable for bindings from Observable objects:**

```swift
struct EditView: View {
    @Bindable var item: Item  // Item is @Observable

    var body: some View {
        TextField("Name", text: $item.name)  // $ works via @Bindable
    }
}
```

### Navigation

**NavigationStack** for hierarchical navigation:

```swift
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationDestination(for: Item.self) { item in
        ItemDetail(item: item)
    }
}
```

**Programmatic navigation**: Append to path, pop by removing.

## Async Patterns in Views

### The `.task` Modifier

Preferred way to run async work tied to view lifecycle:

```swift
.task {
    await viewModel.loadData()
}

// With ID - restarts when ID changes
.task(id: selectedCategory) {
    await viewModel.loadItems(for: selectedCategory)
}
```

### Cancellation

`.task` automatically cancels when view disappears. Check cancellation in long-running work:

```swift
func loadAllPages() async {
    for page in 1...100 {
        guard !Task.isCancelled else { return }
        await loadPage(page)
    }
}
```

### Reacting to Changes

Use `onChange(of:initial:_:)` (iOS 17+) to respond to state changes:

```swift
.onChange(of: searchText, initial: false) { oldValue, newValue in
    // React to change with access to both values
    if newValue.isEmpty {
        results = []
    }
}

// For simple cases where you don't need oldValue
.onChange(of: selection) { _, newValue in
    loadDetails(for: newValue)
}
```

### Haptic Feedback

Use `sensoryFeedback` for haptics tied to state changes:

```swift
.sensoryFeedback(.success, trigger: saveCompleted)
.sensoryFeedback(.impact, trigger: buttonPressed)
.sensoryFeedback(.selection, trigger: selectedItem)
```

### MainActor Isolation

ViewModels should be `@MainActor` since they drive UI:

```swift
@MainActor @Observable
class ViewModel {
    var items: [Item] = []
    
    func load() async {
        items = try await api.fetchItems()  // Updates UI automatically
    }
}
```

For async patterns, actor isolation, and debugging concurrency issues, see [swift-concurrency.md](references/swift-concurrency.md).

## Performance

### Avoiding Unnecessary Redraws

1. **Extract subviews** that depend on specific state
2. **Use `@Observable`** - finer-grained tracking than ObservableObject
3. **Prefer `let` over computed properties** for static data
4. **Use `Equatable` conformance** for custom types in lists
5. **Use `onGeometryChange`** instead of GeometryReader when possible

### Geometry Reading (iOS 16+)

Prefer `onGeometryChange` over `GeometryReader` - it's more efficient and doesn't affect layout:

```swift
// Preferred: reads geometry without affecting layout
.onGeometryChange(for: CGSize.self) { proxy in
    proxy.size
} action: { size in
    containerSize = size
}

// Avoid: GeometryReader affects layout, causes extra passes
GeometryReader { proxy in
    content
        .onAppear { size = proxy.size }
}
```

### List Optimization

```swift
List(items) { item in
    ItemRow(item: item)
}
.listStyle(.plain)  // Simpler than inset grouped

// For large datasets
LazyVStack {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
```

### Profiling

Use Instruments with Time Profiler and SwiftUI templates to identify:
- Slow view body evaluations
- Excessive redraws
- Main thread blocking

For CLI-based profiling workflow with `xctrace`, see [instruments-cli.md](references/instruments-cli.md).

## Platform-Specific Patterns

### macOS

- Use `Settings` scene for preferences
- `@FocusedValue` for menu bar commands
- `commands` modifier for keyboard shortcuts
- Window management via `WindowGroup`, `Window`, `MenuBarExtra`

### iOS/iPadOS

- `NavigationSplitView` for iPad adaptivity
- `.sheet`, `.fullScreenCover` for modal presentation
- `@Environment(\.horizontalSizeClass)` for adaptive layouts

### Conditional Compilation

```swift
#if os(macOS)
    // macOS-specific
#elseif os(iOS)
    // iOS-specific
#endif
```

## macOS 26 Liquid Glass

For macOS 26+ apps using Liquid Glass design system:

**Key principle**: Glass is for controls and small UI elements, not content surfaces.

```swift
// Correct: glass as background
VStack { content }
    .compositingGroup()
    .background {
        Color.clear.glassEffect(.regular, in: RoundedRectangle(cornerRadius: 16))
    }

// Button styles
Button("Action") { }
    .buttonStyle(.glass)           // Secondary
    .buttonStyle(.glassProminent)  // Primary
```

For complete Liquid Glass implementation patterns, common mistakes, and helper extensions, see [liquid-glass.md](references/liquid-glass.md).

## Common Mistakes

### 1. Blocking Main Thread

```swift
// Wrong: synchronous work in view
var body: some View {
    let data = processLargeFile()  // Blocks UI
}

// Right: async with loading state
.task { data = await processLargeFile() }
```

### 2. State in Wrong Place

```swift
// Wrong: @State for shared model
@State var sharedModel = Model()  // Each view gets own copy

// Right: pass via environment or binding
@Environment(Model.self) var model
```

### 3. Force Unwrapping Optionals

```swift
// Wrong
Text(item.name!)

// Right
if let name = item.name {
    Text(name)
}
```

### 4. Ignoring View Identity

```swift
// Wrong: unstable IDs cause animation issues
ForEach(items, id: \.self)

// Right: stable unique IDs
ForEach(items, id: \.id)
```
