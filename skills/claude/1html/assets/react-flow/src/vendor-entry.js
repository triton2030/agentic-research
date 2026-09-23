import * as React from "react";
import { createRoot } from "react-dom/client";
import * as XYFlow from "@xyflow/react";
import { Graph as DagreGraph, layout as dagreLayout } from "@dagrejs/dagre";

window.HTMLReactFlowVendor = Object.freeze({
  React,
  createRoot,
  XYFlow,
  dagre: Object.freeze({ Graph: DagreGraph, layout: dagreLayout }),
});
