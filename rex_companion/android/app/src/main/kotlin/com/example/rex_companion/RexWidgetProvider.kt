package com.example.rex_companion

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.widget.RemoteViews
import android.graphics.Color
import es.antonborri.home_widget.HomeWidgetProvider

class RexWidgetProvider : HomeWidgetProvider() {

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray, widgetData: android.content.SharedPreferences) {
        appWidgetIds.forEach { widgetId ->
            val views = RemoteViews(context.packageName, R.layout.rex_widget_layout).apply {
                // Get data from widgetData (SharedPreferences)
                val status = widgetData.getString("status", "SYSTEM LIVE")
                val activity = widgetData.getString("activity", "IDLE")

                setTextViewText(R.id.widget_status, status)
                setTextViewText(R.id.widget_activity, activity)
                
                // Optional: Change colors based on status
                if (status?.contains("ERROR", ignoreCase = true) == true) {
                    setTextColor(R.id.widget_status, Color.RED)
                } else {
                    setTextColor(R.id.widget_status, Color.WHITE)
                }
            }
            appWidgetManager.updateAppWidget(widgetId, views)
        }
    }
}
