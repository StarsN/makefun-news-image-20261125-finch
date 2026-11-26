// news-image-20261125: ship the finished front page to the output directory.
// Node 22, standard library only. No network, no randomness: the output
// bytes are exactly the bytes of entry.png in this repository, so repeated
// runs write identical files.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = join(here, "entry.png");

// Refuse to ship a corrupt file: a PNG starts with its 8-byte signature,
// and the gate caps an entry at 1 MiB (1048576 bytes).
const data = readFileSync(src);
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!data.subarray(0, 8).equals(pngMagic)) {
  throw new Error("entry.png is not a PNG file");
}
if (data.length > 1048576) {
  throw new Error(`entry.png is ${data.length} bytes, over the 1 MiB gate limit`);
}
// The gate also caps the image at 1024 by 1024 pixels: read the IHDR
// width and height (big-endian uint32 at offsets 16 and 20).
const width = data.readUInt32BE(16);
const height = data.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 gate limit`);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "entry.png"));
// Confirm the copy landed byte for byte: the grader runs the program
// twice and the two outputs must be identical.
const written = readFileSync(join(outDir, "entry.png"));
if (!written.equals(data)) {
  throw new Error("copied entry.png differs from the repository file");
}
console.log(`wrote entry.png (${data.length} bytes, ${width}x${height}) to ${outDir}`);
