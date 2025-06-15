package com.example.adkreceiver;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.usb.*;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "ADKReceiver";
    private static final String ACTION_USB_PERMISSION = "com.example.adkreceiver.USB_PERMISSION";
    
    private UsbManager usbManager;
    private UsbDevice device;
    private UsbDeviceConnection connection;
    private UsbInterface intf;
    private UsbEndpoint endpointIn;
    private UsbEndpoint endpointOut;
    
    private TextView receivedDataText;
    private PendingIntent permissionIntent;
    
    private final BroadcastReceiver usbReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (ACTION_USB_PERMISSION.equals(action)) {
                synchronized (this) {
                    UsbDevice device = intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);
                    if (intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)) {
                        if (device != null) {
                            connectToDevice(device);
                        }
                    } else {
                        Log.d(TAG, "Permission denied for device " + device);
                    }
                }
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        receivedDataText = findViewById(R.id.receivedDataText);
        
        // Initialize USB manager
        usbManager = (UsbManager) getSystemService(Context.USB_SERVICE);
        permissionIntent = PendingIntent.getBroadcast(this, 0, new Intent(ACTION_USB_PERMISSION), 0);
        
        // Register for USB events
        IntentFilter filter = new IntentFilter(ACTION_USB_PERMISSION);
        registerReceiver(usbReceiver, filter);
        
        // Check for connected devices
        checkForDevices();
    }
    
    private void checkForDevices() {
        for (UsbDevice device : usbManager.getDeviceList().values()) {
            // Request permission for the device
            usbManager.requestPermission(device, permissionIntent);
        }
    }
    
    private void connectToDevice(UsbDevice device) {
        this.device = device;
        
        // Find the interface and endpoints
        intf = device.getInterface(0);
        for (int i = 0; i < intf.getEndpointCount(); i++) {
            UsbEndpoint endpoint = intf.getEndpoint(i);
            if (endpoint.getDirection() == UsbConstants.USB_DIR_IN) {
                endpointIn = endpoint;
            } else {
                endpointOut = endpoint;
            }
        }
        
        // Open connection
        connection = usbManager.openDevice(device);
        if (connection != null) {
            connection.claimInterface(intf, true);
            Toast.makeText(this, "Connected to device", Toast.LENGTH_SHORT).show();
            
            // Start reading data
            startReading();
        }
    }
    
    private void startReading() {
        new Thread(() -> {
            byte[] buffer = new byte[64];
            while (true) {
                int bytesRead = connection.bulkTransfer(endpointIn, buffer, buffer.length, 5000);
                if (bytesRead > 0) {
                    final String receivedData = new String(buffer, 0, bytesRead);
                    runOnUiThread(() -> {
                        receivedDataText.setText("Received: " + receivedData);
                        Toast.makeText(MainActivity.this, "Received: " + receivedData, Toast.LENGTH_SHORT).show();
                    });
                }
            }
        }).start();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(usbReceiver);
        if (connection != null) {
            connection.close();
        }
    }
} 