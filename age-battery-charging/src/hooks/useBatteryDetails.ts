import { useCallback, useEffect, useState } from 'react';
import NativeBatteryDetails, {
  type BatteryDetails as Details,
} from '../../modules/my-module';

const EMPTY: Details = {
  voltageMv: -1,
  currentMa: -1,
  capacityMah: -1,
  designCapacityMah: -1,
  chargeCounterMah: -1,
  chargeTimeRemainingMs: -1,
  temperatureC: -1,
  health: 'UNKNOWN',
  plugged: 'UNPLUGGED',
  level: -1,
};

export function useBatteryDetails() {
  const [details, setDetails] = useState<Details>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const result = await NativeBatteryDetails.getDetailsAsync();
      setDetails(result);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Native battery readings unavailable.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void Promise.resolve().then(refresh);
  }, [refresh]);

  return { details, loading, error, refresh };
}
