import { NativeModule } from 'expo';

export type BatteryDetails = {
  voltageMv: number;
  currentMa: number;
  capacityMah: number;
  designCapacityMah: number;
  chargeCounterMah: number;
  temperatureC: number;
  health: string;
  plugged: string;
  level: number;
};

export interface BatteryDetailsModule extends NativeModule {
  getDetailsAsync(): Promise<BatteryDetails>;
}
