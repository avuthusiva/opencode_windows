import * as Battery from 'expo-battery';
import { colors } from '../constants/theme';

export function batteryPercent(level: number): string {
  if (level < 0) return '--';
  return `${Math.round(level * 100)}%`;
}

export function stateLabel(state: Battery.BatteryState): string {
  switch (state) {
    case Battery.BatteryState.CHARGING:
      return 'Charging';
    case Battery.BatteryState.FULL:
      return 'Full';
    case Battery.BatteryState.UNPLUGGED:
      return 'On battery';
    case Battery.BatteryState.NOT_CHARGING:
      return 'Plugged in, not charging';
    default:
      return 'Unknown';
  }
}

export function stateColor(state: Battery.BatteryState): string {
  switch (state) {
    case Battery.BatteryState.CHARGING:
      return colors.primary;
    case Battery.BatteryState.FULL:
      return colors.info;
    case Battery.BatteryState.UNPLUGGED:
      return colors.warning;
    case Battery.BatteryState.NOT_CHARGING:
      return colors.danger;
    default:
      return colors.muted;
  }
}

export function fillColor(level: number): string {
  if (level < 0) return colors.muted;
  if (level <= 0.15) return colors.danger;
  if (level <= 0.3) return colors.warning;
  return colors.primary;
}

export function timeLabel(timestamp: number): string {
  if (!timestamp) return '--';
  return new Date(timestamp).toLocaleTimeString();
}

type DetailsForEstimate = {
  capacityMah: number;
  currentMa: number;
};

export function timeToFull(
  details: DetailsForEstimate,
  level: number,
  charging: boolean
): string {
  if (!charging) return 'Not charging';
  if (details.capacityMah <= 0 || details.currentMa <= 0 || level < 0) {
    return 'Unavailable';
  }

  const remainingMah = (1 - level) * details.capacityMah;
  const minutes = Math.round((remainingMah / details.currentMa) * 60);
  if (!Number.isFinite(minutes) || minutes < 0) return 'Unavailable';
  if (minutes === 0) return 'Full';

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return hours > 0 ? `${hours} h ${mins} min` : `${mins} min`;
}

export function durationLabel(milliseconds: number): string {
  if (milliseconds <= 0) return 'Unavailable';
  const minutes = Math.round(milliseconds / 60000);
  if (minutes < 1) return 'Less than 1 min';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return hours > 0 ? `${hours} h ${mins} min` : `${mins} min`;
}

export function voltageLabel(voltageMv: number): string {
  return voltageMv > 0 ? `${(voltageMv / 1000).toFixed(2)} V` : 'Unavailable';
}

export function currentLabel(currentMa: number): string {
  return currentMa > 0 ? `${currentMa.toFixed(0)} mA` : 'Unavailable';
}

export function capacityLabel(capacityMah: number): string {
  return capacityMah > 0 ? `${Math.round(capacityMah)} mAh` : 'Unavailable';
}
