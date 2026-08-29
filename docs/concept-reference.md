# 13. Homebox Setup & Labeling Strategy

## Overview
This document outlines the strategy for managing home inventory using Homebox, specifically focusing on the label sizing, physical materials, and Asset ID reservation system to ensure a smooth workflow.

## Asset ID Allocation Strategy
Homebox utilizes a `000-000` asset ID format. To accommodate a hybrid approach of using pre-printed label sheets and on-demand printing, we reserve specific ID blocks. 

The Homebox auto-increment counter must be bumped up to **`500-000`** upon initial setup. This leaves the lower ID blocks completely free for our pre-printed sheets, avoiding any accidental collisions when adding new "uncategorized" items on the fly.

### Reserved ID Blocks
*   **`000-000` to `100-000`**: Reserved for **Small Labels** (Electronics).
*   **`100-001` to `200-000`**: Reserved for **Medium/Large Labels** (Furniture, Tool Cases, Bins).
*   **`500-000` and above**: Auto-incrementing block for **Regular Items** printed on-demand with item-specific details.

## Label Sizing and Usage
Different items require different label sizes based on physical constraints and scannability.

1.  **Small Electronics & Components**
    *   **Size:** 0.5" x 0.5"  
    *   **Workflow:** Pre-print 1-2 sheets of these QR codes. When a new small item is acquired, stick a label on it, scan with a phone, and add the item details to Homebox.
2.  **Furniture, Tool Cases, & Medium Items**
    *   **Size:** Standard address label size (e.g., 1" x 2.625") or 2" x 3".
    *   **Workflow:** These can be printed on-demand.
3.  **Garage Bins & Large Storage**
    *   **Size:** Shipping label size (4" x 6") or half-sheet (5.5" x 8.5").
    *   **Workflow:** Pre-printed with giant QR codes to allow scanning from across the garage.
4.  **Locations (Shelves, Rooms)**
    *   **Workflow:** Location labels should be visually distinct from item labels (e.g., add a bold border or use a different color) so that when scanning, it's immediately obvious that a location is being scanned rather than a stored item.

## Printing & Materials
All labels are printed using the **CP-2024 Color Laser Printer**. 

**Material Selection:**
*   For indoor, climate-controlled items: Standard paper laser labels are sufficient.
*   For garage items (bins, tools): **Weatherproof polyester laser labels** are highly recommended. Standard paper labels will absorb ambient moisture in a garage environment, causing them to peel or degrade over time. Polyester labels fuse with the laser toner to create a durable, waterproof tag.

## Custom Label Generation
Labels are generated using a dedicated external Python script (managed via a Git submodule in `./external`). 

*   **URL Format:** QR codes encode a shortlink using the format `http://ag4.in/a{id}` (e.g., asset ID `000-010` becomes `ag4.in/a10`). This relies on a Traefik redirect rule to point to the correct Homebox item.
*   **Authentication:** The generation script pulls credentials (`HOMEBOX_URL`, `HOMEBOX_TOKEN`, `QR_CODE_PREFIX`) from an environment-provided file decrypted via `sops`.
*   **Workflow Automation:** The script can query the Homebox API for items tagged `#needs-label`, generate the appropriate Avery 5160 PDF, and automatically re-tag them as `#label-printed`.
