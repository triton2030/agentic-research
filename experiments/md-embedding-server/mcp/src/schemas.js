import { z } from "zod";

export const PathArg = z.string().min(1).describe("Filesystem path");
export const CorpusArg = z.string().min(1).describe("Path to corpus root (folder containing .md files)");
export const HeadingLevel = z.number().int().min(1).max(6);
export const PathGlobs = z.array(z.string().min(1)).optional();
export const LimitArg = z.number().int().positive().max(200).optional();
