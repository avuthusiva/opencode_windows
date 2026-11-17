package expo.modules.mymodule

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import kotlin.math.abs

class BatteryDetailsModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("BatteryDetails")

    AsyncFunction("getDetailsAsync") {
      val context = appContext.reactContext
      if (context == null) {
        return@AsyncFunction emptyResult()
      }

      try {
        val intent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val manager = context.getSystemService(Context.BATTERY_SERVICE) as? BatteryManager

        val rawLevel = intent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = intent?.getIntExtra(BatteryManager.EXTRA_SCALE, 100) ?: 100
        val level = if (rawLevel >= 0 && scale > 0) rawLevel.toDouble() / scale else -1.0

        val voltageMv = intent?.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1) ?: -1
        val temperatureTenths = intent?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1) ?: -1
        val temperatureC = if (temperatureTenths > 0) temperatureTenths / 10.0 else -1.0

        val healthValue = intent?.getIntExtra(
          BatteryManager.EXTRA_HEALTH,
          BatteryManager.BATTERY_HEALTH_UNKNOWN
        ) ?: BatteryManager.BATTERY_HEALTH_UNKNOWN
        val health = when (healthValue) {
          BatteryManager.BATTERY_HEALTH_GOOD -> "GOOD"
          BatteryManager.BATTERY_HEALTH_OVERHEAT -> "OVERHEAT"
          BatteryManager.BATTERY_HEALTH_DEAD -> "DEAD"
          BatteryManager.BATTERY_HEALTH_OVER_VOLTAGE -> "OVER_VOLTAGE"
          BatteryManager.BATTERY_HEALTH_UNSPECIFIED_FAILURE -> "UNSPECIFIED_FAILURE"
          BatteryManager.BATTERY_HEALTH_COLD -> "COLD"
          else -> "UNKNOWN"
        }

        val pluggedValue = intent?.getIntExtra(BatteryManager.EXTRA_PLUGGED, 0) ?: 0
        val plugged = when (pluggedValue) {
          BatteryManager.BATTERY_PLUGGED_AC -> "AC"
          BatteryManager.BATTERY_PLUGGED_USB -> "USB"
          BatteryManager.BATTERY_PLUGGED_WIRELESS -> "WIRELESS"
          else -> "UNPLUGGED"
        }

        var currentMa = -1.0
        var chargeCounterMah = -1.0
        var chargeTimeRemainingMs = -1L
        if (manager != null) {
          try {
            val microAmps = manager.getLongProperty(BatteryManager.BATTERY_PROPERTY_CURRENT_NOW)
            if (microAmps != Long.MIN_VALUE && microAmps != 0L) {
              currentMa = abs(microAmps.toDouble()) / 1000.0
            }
            val microAh = manager.getLongProperty(BatteryManager.BATTERY_PROPERTY_CHARGE_COUNTER)
            if (microAh > 0) {
              chargeCounterMah = microAh / 1000.0
            }
            chargeTimeRemainingMs = manager.computeChargeTimeRemaining()
          } catch (e: Exception) {
            // Some devices do not implement these properties.
          }
        }

        val designMicroAh = readLong("/sys/class/power_supply/battery/charge_full_design")
        val designCapacityMah = if (designMicroAh != null && designMicroAh > 0) {
          designMicroAh / 1000.0
        } else {
          -1.0
        }
        val capacityMah = if (chargeCounterMah > 0 && level > 0) {
          chargeCounterMah / level
        } else {
          designCapacityMah
        }

        return@AsyncFunction mapOf(
          "voltageMv" to voltageMv.toDouble(),
          "currentMa" to currentMa,
          "capacityMah" to capacityMah,
          "designCapacityMah" to designCapacityMah,
          "chargeCounterMah" to chargeCounterMah,
          "chargeTimeRemainingMs" to chargeTimeRemainingMs.toDouble(),
          "temperatureC" to temperatureC,
          "health" to health,
          "plugged" to plugged,
          "level" to level
        )
      } catch (e: Exception) {
        return@AsyncFunction emptyResult()
      }
    }
  }

  private fun readLong(path: String): Long? = try {
    java.io.File(path).readText().trim().toLongOrNull()
  } catch (e: Exception) {
    null
  }

  private fun emptyResult(): Map<String, Any> = mapOf(
    "voltageMv" to -1.0,
    "currentMa" to -1.0,
    "capacityMah" to -1.0,
    "designCapacityMah" to -1.0,
    "chargeCounterMah" to -1.0,
    "chargeTimeRemainingMs" to -1.0,
    "temperatureC" to -1.0,
    "health" to "UNKNOWN",
    "plugged" to "UNPLUGGED",
    "level" to -1.0
  )
}
