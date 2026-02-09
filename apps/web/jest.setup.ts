import "@testing-library/jest-dom";
import { TextDecoder, TextEncoder } from "util";

if (!global.TextEncoder) {
  // Firebase/undici require TextEncoder in Jest's jsdom runtime.
  (globalThis as any).TextEncoder = TextEncoder;
}

if (!global.TextDecoder) {
  (globalThis as any).TextDecoder = TextDecoder;
}
