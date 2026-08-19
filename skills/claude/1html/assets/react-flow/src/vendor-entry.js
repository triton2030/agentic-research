import * as React from "react";
import { createRoot } from "react-dom/client";
import * as XYFlow from "@xyflow/react";

window.HTMLReactFlowVendor = Object.freeze({ React, createRoot, XYFlow });
