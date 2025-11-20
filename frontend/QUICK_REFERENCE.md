# shadcn/ui Quick Reference Card

## 🚀 Quick Start

```bash
cd frontend
npm run dev  # Start dev server at http://localhost:3000
```

## 📦 Installed Components

| Component | Path | Import |
|-----------|------|--------|
| Button | `components/ui/button.tsx` | `import { Button } from '@/components/ui/button'` |
| Card | `components/ui/card.tsx` | `import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'` |
| Input | `components/ui/input.tsx` | `import { Input } from '@/components/ui/input'` |

## 🎨 Button Variants

```tsx
<Button variant="default">Default</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon">🔥</Button>
```

## 🃏 Card Usage

```tsx
<Card>
  <CardHeader>
    <CardTitle>Title Here</CardTitle>
    <CardDescription>Subtitle here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Your content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

## 📝 Input Usage

```tsx
<Input placeholder="Enter text..." />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" />
<Input disabled placeholder="Disabled" />
```

## 🎨 Utility Function

```tsx
import { cn } from '@/lib/utils'

<div className={cn(
  "base-class",
  condition && "conditional-class",
  props.className
)} />
```

## ➕ Add More Components

```bash
# Add a single component
npx shadcn-ui@latest add dialog

# Add multiple components
npx shadcn-ui@latest add dialog alert toast
```

## 🎨 Common Tailwind Classes

### Layout
- `flex`, `grid`, `block`, `inline-block`
- `flex-col`, `flex-row`
- `justify-center`, `items-center`
- `gap-2`, `gap-4`, `gap-8`
- `space-x-4`, `space-y-4`

### Sizing
- `w-full`, `h-full`
- `max-w-4xl`, `max-w-6xl`
- `min-h-screen`
- `p-4`, `px-6`, `py-8`
- `m-4`, `mx-auto`, `my-8`

### Colors (using CSS variables)
- `bg-background`, `text-foreground`
- `bg-primary`, `text-primary-foreground`
- `bg-secondary`, `text-secondary-foreground`
- `bg-muted`, `text-muted-foreground`
- `bg-destructive`, `text-destructive-foreground`
- `border-border`

### Typography
- `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`
- `font-normal`, `font-medium`, `font-semibold`, `font-bold`
- `text-center`, `text-left`, `text-right`

### Effects
- `rounded-md`, `rounded-lg`
- `shadow-sm`, `shadow-md`, `shadow-lg`
- `hover:bg-accent`
- `focus:ring-2`
- `transition-colors`

## 🌙 Dark Mode Classes

```tsx
// Light and dark mode
<div className="bg-white dark:bg-slate-900">
  <p className="text-slate-900 dark:text-white">Text</p>
</div>
```

## 📱 Responsive Design

```tsx
// Mobile first approach
<div className="text-sm md:text-base lg:text-lg">
  Responsive text
</div>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  Responsive grid
</div>
```

## 🎯 Common Patterns

### Form with Input and Button
```tsx
<div className="flex gap-2">
  <Input placeholder="Enter message..." />
  <Button>Send</Button>
</div>
```

### Card with Actions
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Content</p>
  </CardContent>
  <CardFooter className="flex gap-2">
    <Button variant="outline">Cancel</Button>
    <Button>Confirm</Button>
  </CardFooter>
</Card>
```

### Loading State
```tsx
<Button disabled>
  Loading...
</Button>
```

### Icon Button
```tsx
import { Trash2 } from 'lucide-react'

<Button size="icon" variant="ghost">
  <Trash2 className="h-4 w-4" />
</Button>
```

## 🔥 Pro Tips

1. **Use `cn()` for conditional classes**
   ```tsx
   className={cn("base", isActive && "active")}
   ```

2. **Leverage CSS variables for theming**
   ```css
   background-color: hsl(var(--primary));
   ```

3. **Compose components**
   ```tsx
   <Button asChild>
     <Link href="/about">About</Link>
   </Button>
   ```

4. **Use Lucide icons**
   ```tsx
   import { Check, X, Loader2 } from 'lucide-react'
   ```

5. **Extend components**
   ```tsx
   const MyButton = ({ children, ...props }) => (
     <Button className="custom-class" {...props}>
       {children}
     </Button>
   )
   ```

## 📚 Resources

- [shadcn/ui Components](https://ui.shadcn.com/docs/components)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Lucide Icons](https://lucide.dev/icons)
- [Radix UI](https://www.radix-ui.com/)

## 🆘 Troubleshooting

**Build fails?**
```bash
rm -rf .next node_modules
npm install
npm run build
```

**Styles not applying?**
- Check `globals.css` is imported in `layout.tsx`
- Verify Tailwind config paths include your files
- Clear browser cache

**Component not found?**
- Check import path uses `@/` alias
- Verify component file exists in `components/ui/`
- Restart dev server

---

**Quick Command Reference:**
```bash
npm run dev      # Start development
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run linter
```

Happy coding! 🎉

