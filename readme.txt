# Shopify Chatbot

A modern, professional chatbot web application built with Next.js, React, and Tailwind CSS, designed to assist users with product inquiries, order tracking, and store policies for Shopify-based stores.

## Features

- **Conversational UI:** Chatbot interface for users to ask questions about products, orders, and store policies.
- **Session Management:** User sessions are managed and persisted in local storage, with automatic session expiration after 24 hours.
- **Suggestion Chips:** Quick-access suggestion buttons for common queries.
- **Rich UI Components:** Built with a comprehensive set of reusable UI components (cards, dialogs, avatars, etc.).
- **API Integration:** Backend API route proxies requests to an external chatbot service.
- **Responsive Design:** Fully responsive and styled with Tailwind CSS.
- **Dark Mode Support:** Themeable with light and dark modes.

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts         # API route for chat requests
│   │   ├── globals.css              # Global styles (Tailwind CSS)
│   │   ├── layout.tsx               # Root layout component
│   │   ├── page.tsx                 # Main chatbot page
│   │   └── page-copy.tsx            # Alternative chatbot page (variant)
│   ├── components/
│   │   ├── theme-provider.tsx
│   │   └── ui/                      # Reusable UI components (buttons, cards, dialogs, etc.)
│   ├── hooks/                       # Custom React hooks
│   ├── lib/
│   │   └── utils.ts                 # Utility functions
│   ├── public/                      # Static assets (images, logos)
│   ├── styles/                      # Additional styles
│   ├── package.json                 # Project metadata and dependencies
│   ├── tailwind.config.ts           # Tailwind CSS configuration
│   ├── next.config.mjs              # Next.js configuration
│   └── tsconfig.json                # TypeScript configuration
```

## Getting Started

### Prerequisites

- Node.js (v18+ recommended)
- pnpm, npm, or yarn

### Installation

1. **Install dependencies:**
   ```bash
   pnpm install
   # or
   npm install
   # or
   yarn install
   ```

2. **Run the development server:**
   ```bash
   pnpm dev
   # or
   npm run dev
   # or
   yarn dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
pnpm build
pnpm start
# or use npm/yarn equivalents
```

## Configuration

- **API Endpoint:** The chatbot backend proxies requests to an external API. Update the endpoint in `app/api/chat/route.ts` as needed.
- **Environment Variables:** If using a custom API URL, set `NEXT_PUBLIC_API_URL` in your environment.

## Core Files

- **`app/page.tsx`**: Main chatbot UI, handles session, message state, suggestions, and API calls.
- **`app/api/chat/route.ts`**: Next.js API route that forwards chat messages to an external chatbot API with timeout and error handling.
- **`components/ui/`**: Rich set of UI components (cards, dialogs, buttons, etc.) for building the interface.
- **`lib/utils.ts`**: Utility for merging Tailwind CSS class names.

## Styling

- **Tailwind CSS** is used for all styling, with custom themes and dark mode support.
- **Global styles** are defined in `app/globals.css`.
- **Component-level styles** are handled via Tailwind utility classes.

## Customization

- **UI Components:** Extend or modify components in `components/ui/` for custom look and feel.
- **Chatbot Logic:** Adjust session management, message formatting, or API integration in `app/page.tsx`.
- **Theme:** Update `tailwind.config.ts` and CSS variables in `app/globals.css` for branding.

## Dependencies

- **React 19**
- **Next.js 15**
- **Tailwind CSS 3**
- **Radix UI** (for accessible UI primitives)
- **Lucide React** (icon library)
- **Other:** react-hook-form, zod, recharts, embla-carousel, and more (see `package.json`).

## License

This project is for demonstration and internal use. Please check with the project owner for licensing details.

## Backend Access

This project is designed to work with a separate backend service that handles chatbot logic and Shopify integration. You can find a reference backend implementation here:

[Shopify Chatbot Backend (GitHub)](https://github.com/ahmedriaz12/Shopify-chatbot-backend.git)

### Setting Up the Backend

1. **Clone the backend repository:**
   ```bash
   git clone https://github.com/ahmedriaz12/Shopify-chatbot-backend.git
   cd Shopify-chatbot-backend
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the backend server:**
   ```bash
   python main.py
   ```
   (You may need to activate a virtual environment first, e.g., `source venv/bin/activate`)

4. **Configure the frontend to use your backend:**
   - Update the API endpoint in your frontend's `app/api/chat/route.ts` or set the `NEXT_PUBLIC_API_URL` environment variable to point to your backend server (e.g., `http://localhost:8000`).

For more details, see the backend repository's documentation: [Shopify Chatbot Backend](https://github.com/ahmedriaz12/Shopify-chatbot-backend.git) 