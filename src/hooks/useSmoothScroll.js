import { useEffect } from "react";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * useSmoothScroll
 * Initialises Lenis smooth scroll synced with GSAP ScrollTrigger.
 * Attach to a specific scroll container so smooth scrolling stays scoped to
 * the chatbot workspace.
 *
 * @param {object} options  - Optional Lenis config overrides
 */
export function useSmoothScroll(wrapperRef, options = {}) {
  useEffect(() => {
    const wrapper = wrapperRef?.current;
    if (!wrapper) return undefined;

    const previousDefaults = ScrollTrigger.defaults();
    const lenis = new Lenis({
      wrapper,
      content: wrapper.firstElementChild || wrapper,
      eventsTarget: wrapper,
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: "vertical",
      gestureOrientation: "vertical",
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
      ...options,
    });

    // Sync Lenis scroll position to GSAP ScrollTrigger
    lenis.on("scroll", ScrollTrigger.update);

    // Keep ScrollTrigger measurements attached to the chat's own scroll area.
    ScrollTrigger.scrollerProxy(wrapper, {
      scrollTop(value) {
        if (arguments.length) {
          lenis.scrollTo(value, { immediate: true });
        }
        return wrapper.scrollTop;
      },
      getBoundingClientRect() {
        return wrapper.getBoundingClientRect();
      },
      pinType: wrapper.style.transform ? "transform" : "fixed",
    });
    ScrollTrigger.defaults({ ...previousDefaults, scroller: wrapper });

    // Drive Lenis from GSAP's ticker so both stay in sync.
    const tick = (time) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);

    return () => {
      lenis.destroy();
      gsap.ticker.remove(tick);
      ScrollTrigger.defaults(previousDefaults);
      ScrollTrigger.scrollerProxy(wrapper, null);
      ScrollTrigger.refresh();
    };
  }, [wrapperRef]);
}
