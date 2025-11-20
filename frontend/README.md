# Next.js Frontend

A modern Next.js frontend application with TypeScript.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file (optional):
```bash
cp .env.example .env.local
```

3. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Features

- Next.js 14 with App Router
- TypeScript support
- **shadcn/ui** - Beautiful, accessible component library
- **Tailwind CSS** - Utility-first CSS framework
- Modern, responsive UI
- API integration with Flask backend
- Hot reload in development

## shadcn/ui Setup

This project uses [shadcn/ui](https://ui.shadcn.com/) for UI components. The setup includes:

- ✅ Tailwind CSS configured
- ✅ CSS variables for theming
- ✅ Dark mode support
- ✅ Component library structure

### Adding New Components

To add more shadcn/ui components, use the CLI:

```bash
npx shadcn-ui@latest add [component-name]
```

Examples:
```bash
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add form
npx shadcn-ui@latest add dropdown-menu
```

### Available Components

Currently installed components:
- Button
- Card (with CardHeader, CardTitle, CardDescription, CardContent, CardFooter)

### Customization

- **Theme colors**: Edit CSS variables in `app/globals.css`
- **Tailwind config**: Modify `tailwind.config.ts`
- **Component styles**: Components are in `components/ui/`

