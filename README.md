# vrappcommon

Shared utilities for VR Python applications — async OSC dispatching, OpenVR init, VRChat OSC setup, error GUI helpers, and common math/utils.

Used by:
- [vr_audience_fire](https://github.com/Python1320/vr_audience_fire)
- [vr_asmr_petting](https://github.com/Python1320/vr_asmr_petting)

## Modules

| Module | Description |
|---|---|
| `AsyncOSCDispatcher` | Async-capable OSC message dispatcher with per-address serial queues |
| `openvrutils` | Async OpenVR initialization with auto-retry |
| `vrutils` | VRChat OSC server setup with zeroconf registration |
| `jankyguihelpers` | Error windows, console allocation, single-instance guards |
| `task_helper` | Fire-and-forget asyncio task spawning with error handling |
| `utils` | `clamp`, `remap`, `oscfloat`, and re-exports |

## Usage

```python
from vrappcommon import vrutils, openvrutils, AsyncOSCDispatcher
```
