
## fboxaha for Python

Easy Fritz!BOX HTTP AHA access in Python:

    fb = FritzAHA('fritz.box', username='', password='LocalAccessPassword')
    
    devices = fb.power_devices
    
    for device in devices:
        dev = device[0]
        print("Consumption: ", fb.get_last_consumption(dev))

### Resources

Loosly based on [valpo / fritzbox](https://github.com/valpo/fritzbox).

