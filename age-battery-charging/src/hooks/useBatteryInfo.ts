import * as Battery from 'expo-battery';
import { useCallback, useEffect, useState } from 'react';
import { batteryPercent, timeLabel } from '../utils/battery';

export type BatteryInfo = {
  level: number;
  state: Battery.BatteryState;
  lowPowerMode: boolean;
  updatedAt: number;
};

export type Reading = {
  id: number;
  percent: string;
  time: string;
};

const UNKNOWN: BatteryInfo = {
  level: -1,
  state: Battery.BatteryState.UNKNOWN,
  lowPowerMode: false,
  updatedAt: 0,
};

export function useBatteryInfo() {
  const [info, setInfo] = useState<BatteryInfo>(UNKNOWN);
  const [history, setHistory] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const power = await Battery.getPowerStateAsync();
      const updatedAt = Date.now();
      const next: BatteryInfo = {
        level: power.batteryLevel,
        state: power.batteryState,
        lowPowerMode: power.lowPowerMode,
        updatedAt,
      };

      setInfo(next);
      setHistory((previous) => {
        if (next.level < 0) return previous;
        const percent = batteryPercent(next.level);
        if (previous[0]?.percent === percent) return previous;
        return [
          { id: updatedAt, percent, time: timeLabel(updatedAt) },
          ...previous,
        ].slice(0, 10);
      });
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not read battery information.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Defer the first read so state updates happen asynchronously after mount.
    void Promise.resolve().then(refresh);

    const subscriptions = [
      Battery.addBatteryLevelListener(() => refresh()),
      Battery.addBatteryStateListener(() => refresh()),
      Battery.addLowPowerModeListener(() => refresh()),
    ];

    return () => {
      for (const subscription of subscriptions) {
        subscription.remove();
      }
    };
  }, [refresh]);

  return { info, history, loading, error, refresh };
}
