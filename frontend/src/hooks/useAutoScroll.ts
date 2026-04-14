import { useEffect, type RefObject } from "react";

export function useAutoScroll<T extends HTMLElement>(
  ref: RefObject<T | null>,
  deps: unknown[],
) {
  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    el.scrollTop = el.scrollHeight;
  }, deps);
}