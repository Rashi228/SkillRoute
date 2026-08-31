import '@testing-library/jest-dom';

// ResizeObserver is not available in jsdom; stub it so @react-three/fiber doesn't throw.
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
