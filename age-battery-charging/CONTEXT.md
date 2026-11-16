# AGE Battery Charging — Project Context

Last updated: 2026-11-16

## What this app is

An Android-first Expo / React Native app that monitors the phone's battery.

- App name: **AGE Battery Charging**
- Project folder: `C:\Users\asvr4\Desktop\work\opencode\age-battery-charging`
- Expo SDK: **58.0.0**
- React Native: 0.88.1
- React: 19.3.0
- Language: TypeScript
- Navigation: Expo Router (file-based, routes in `src/app/`)

## Features

### Battery tab (`src/app/index.tsx`)
- Battery level percentage with a coloured bar (red <= 15%, amber <= 30%, green above)
- Charging state: Charging / Full / On battery / Plugged in, not charging
- Low power mode on/off
- Last updated time and a Refresh button

### Details tab (`src/app/details.tsx`)
- Battery level, charging status, low power mode
- Battery optimization status (Android)
- Time to full — **estimated**, not a system value
- Battery health
- Charging current (mA)
- Charging voltage (V)
- Battery capacity and design capacity (mAh)
- Battery temperature (C)
- Power source (AC / USB / wireless / unplugged)
- Last 10 readings collected during the current session

## Code layout

```
src/
  app/
    _layout.tsx            tab navigator (Battery / Details)
    index.tsx              Battery screen
    details.tsx            Details screen
  components/
    InfoRow.tsx            label/value row used by both screens
  hooks/
    useBatteryInfo.ts      standard Expo battery data + listeners + reading history
    useBatteryDetails.ts   native battery readings from the local module
  utils/
    battery.ts             labels, colours, time-to-full estimate
  constants/
    theme.ts               dark theme colours and spacing
modules/
  my-module/               local Expo native module (Android only)
    index.ts               JS entry, exports native module
    src/BatteryDetailsModule.ts   TypeScript type for native result
    android/src/main/java/expo/modules/mymodule/BatteryDetailsModule.kt
    expo-module.config.json
```

## Where the data comes from

- `expo-battery`: level, charging state, low power mode, battery optimization. Works in Expo Go.
- Local native module `BatteryDetails` (Kotlin): reads Android `BatteryManager` and the sticky
  `ACTION_BATTERY_CHANGED` intent for voltage, temperature, health, plugged type, current
  (`BATTERY_PROPERTY_CURRENT_NOW` in microamps) and charge counter. Design capacity is read
  from `/sys/class/power_supply/battery/charge_full_design` where available.
- Values a phone does not report are returned as `-1` and displayed as "Unavailable".

## Important constraints

- The custom native module means **Expo Go cannot run the current app**. A development build
  (APK) is required.
- There is no Android SDK installed on this Windows machine. Builds are done in the cloud with EAS.
- Expo account: `asvr410`
- EAS project: `@asvr410/age-battery-charging`
- Project ID: `009b50d2-9d8f-4a99-8c7c-43bee77c0b95`
- Android package: `com.asvr410.agebatterycharging`
- Deep-link scheme: `agebatterycharging`

## Commands

```bash
npx expo install <package>       # always use this, not npm add
npx expo start                   # dev server (Expo Go only, not for current code)
npx expo lint
npx tsc --noEmit
npx expo-doctor
npx eas-cli@latest build --platform android --profile development
npx eas-cli@latest build:list --limit 3
```

## Build state (as of 2026-11-16)

- Build ID: `227ec37d-625c-48f7-b7eb-56d4693117e0`
- Status at last check: queued in the **free tier** queue, roughly 10 minutes remaining
- Build page: https://expo.dev/accounts/asvr410/projects/age-battery-charging/builds/227ec37d-625c-48f7-b7eb-56d4693117e0
- `eas.json` has a `development` profile: `developmentClient: true`, `distribution: internal`, Android `buildType: apk`
- `expo-dev-client` is installed

## Checks already passing

- `npx tsc --noEmit` — pass
- `npx expo lint` — pass (0 errors)
- `npx expo-doctor` — 20/20 pass
- `npx expo export --platform android` — Android bundle built before the native module was added

## Notes for future changes

- Always follow `AGENTS.md` in this folder: check the Expo SDK version and fetch current
  versioned docs before using Expo/EAS/RN APIs.
- If a new native capability is added, the APK must be rebuilt — over-the-air updates cannot
  change native code.
- Windows Wi-Fi IP changed once during setup (192.168.1.3 -> 192.168.1.2). If using Expo Go
  on a LAN URL, re-check `Get-NetIPAddress` before generating a QR.
- The `App.tsx` and `index.ts` files in the project root are unused template leftovers and were
  intentionally kept.
