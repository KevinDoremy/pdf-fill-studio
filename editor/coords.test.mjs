import assert from "node:assert";
import { pxToPoints, boxPxToPoints } from "./coords.js";

assert.strictEqual(pxToPoints(240, 2.0), 120);

const box = boxPxToPoints({ left: 240, top: 100, width: 400, height: 32 }, 2.0);
assert.deepStrictEqual(box, { x: 120, y: 50, w: 200, h: 16 });

console.log("editor/coords: all tests passed");
