// Entry point for news-image-20261125.
//
// Copies the finished front page (entry.png, next to this file) into the
// directory named by MAKEFUN_OUTPUT_DIR. Fully offline, standard library
// only. Before copying it checks the file is really a PNG, is 1024x1024,
// and is within the 1 MiB limit; after copying it re-reads the target and
// confirms the bytes match the source exactly.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);
const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;
const MAX_BYTES = 1048576;

const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, "entry.png");

function fail(message: string): never {
  throw new Error(message);
}

function readPngSize(bytes: Buffer): { width: number; height: number } {
  if (bytes.length < 33) {
    fail("entry.png is too short to hold a PNG header");
  }
  if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    fail("entry.png is not a PNG file");
  }
  const firstChunk = bytes.subarray(12, 16).toString("ascii");
  if (firstChunk !== "IHDR") {
    fail("entry.png does not start with an IHDR chunk");
  }
  return {
    width: bytes.readUInt32BE(16),
    height: bytes.readUInt32BE(20),
  };
}

function main(): void {
  const outDir = process.env.MAKEFUN_OUTPUT_DIR;
  if (!outDir) {
    fail("MAKEFUN_OUTPUT_DIR is not set");
  }
  const bytes = readFileSync(sourcePath);
  if (bytes.length > MAX_BYTES) {
    fail(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  const { width, height } = readPngSize(bytes);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    fail(`entry.png is ${width}x${height}, expected 1024x1024`);
  }
  const sourceHash = createHash("sha256").update(bytes).digest("hex");
  const outDirResolved = resolve(outDir);
  mkdirSync(outDirResolved, { recursive: true });
  const target = join(outDirResolved, "entry.png");
  if (resolve(target) === resolve(sourcePath)) {
    fail("MAKEFUN_OUTPUT_DIR points at the repository itself; refusing to overwrite the source");
  }
  writeFileSync(target, bytes);
  const copied = readFileSync(target);
  if (copied.length !== bytes.length) {
    fail(
      `copied entry.png is ${copied.length} bytes, expected ${bytes.length}`,
    );
  }
  const copiedHash = createHash("sha256").update(copied).digest("hex");
  if (copiedHash !== sourceHash) {
    fail("copied entry.png does not match the source bytes");
  }
  console.log(
    `copied entry.png (${copied.length} bytes, sha256=${sourceHash}) to ${target}`,
  );
}

main();
