import * as Battery from 'expo-battery';
import { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { InfoRow } from '../components/InfoRow';
import { colors, spacing } from '../constants/theme';
import { useBatteryDetails } from '../hooks/useBatteryDetails';
import { useBatteryInfo } from '../hooks/useBatteryInfo';
import {
  batteryPercent,
  capacityLabel,
  currentLabel,
  stateLabel,
  timeLabel,
  timeToFull,
  voltageLabel,
} from '../utils/battery';

export default function DetailsScreen() {
  const { info, history } = useBatteryInfo();
  const { details } = useBatteryDetails();
  const [optimization, setOptimization] = useState<boolean | null>(null);
  const charging = info.state === Battery.BatteryState.CHARGING;

  useEffect(() => {
    let active = true;
    Battery.isBatteryOptimizationEnabledAsync()
      .then((value) => {
        if (active) setOptimization(value);
      })
      .catch(() => {
        if (active) setOptimization(null);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Details</Text>
      <Text style={styles.subheading}>More about the battery on this device</Text>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Power information</Text>
        <InfoRow label="Battery level" value={batteryPercent(info.level)} />
        <InfoRow label="Charging status" value={stateLabel(info.state)} />
        <InfoRow
          label="Low power mode"
          value={info.lowPowerMode ? 'On' : 'Off'}
          valueColor={info.lowPowerMode ? colors.warning : colors.text}
        />
        <InfoRow
          label="Battery optimization"
          value={
            optimization === null
              ? 'Not available'
              : optimization
                ? 'Enabled'
                : 'Disabled'
          }
        />
        <InfoRow label="Last reading" value={timeLabel(info.updatedAt)} />
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Charging details</Text>
        <InfoRow
          label="Time to full"
          value={timeToFull(details, info.level, charging)}
          valueColor={charging ? colors.primary : colors.muted}
        />
        <InfoRow label="Battery health" value={details.health} />
        <InfoRow label="Charging current" value={currentLabel(details.currentMa)} />
        <InfoRow label="Charging voltage" value={voltageLabel(details.voltageMv)} />
        <InfoRow label="Battery capacity" value={capacityLabel(details.capacityMah)} />
        <InfoRow label="Design capacity" value={capacityLabel(details.designCapacityMah)} />
        <InfoRow label="Temperature" value={
          details.temperatureC > 0 ? `${details.temperatureC.toFixed(1)} C` : 'Unavailable'
        } />
        <InfoRow label="Power source" value={details.plugged} />
        <Text style={styles.noteInline}>
          Time to full is an estimate from capacity and charging current.
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Recent readings (this session)</Text>
        {history.length === 0 ? (
          <Text style={styles.empty}>Collecting readings...</Text>
        ) : (
          history.map((reading) => (
            <InfoRow
              key={reading.id}
              label={reading.time}
              value={reading.percent}
              valueColor={colors.primary}
            />
          ))
        )}
      </View>

      <View style={styles.note}>
        <Text style={styles.noteText}>
          Battery temperature, voltage and health are not exposed by the standard
          Expo battery API. They need a custom native module and a development build.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: spacing.xl,
  },
  heading: {
    color: colors.text,
    fontSize: 26,
    fontWeight: '800',
    marginTop: spacing.sm,
  },
  subheading: {
    color: colors.muted,
    fontSize: 14,
    marginBottom: spacing.lg,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '700',
    marginBottom: spacing.sm,
  },
  empty: {
    color: colors.muted,
    fontSize: 14,
    paddingVertical: spacing.sm,
  },
  noteInline: {
    color: colors.muted,
    fontSize: 12,
    marginTop: spacing.sm,
  },
  note: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: 12,
    padding: spacing.md,
  },
  noteText: {
    color: colors.muted,
    fontSize: 13,
    lineHeight: 19,
  },
});
