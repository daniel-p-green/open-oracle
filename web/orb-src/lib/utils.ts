// Minimal class joiner. The registry's cn() uses clsx + tailwind-merge; this page has no Tailwind.
export function cn(...inputs: Array<string | false | null | undefined>) {
  return inputs.filter(Boolean).join(" ");
}
