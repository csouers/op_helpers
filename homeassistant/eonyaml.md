## Adding to homeassistant
My home assistant configuration has the **sensors:** broken out into its own folder. Include **sensor: !include_dir_list sensors** in your **configuration.yaml**. If you also do so, copy the **eon.yaml** file there, and then change the entity that you're sending from your eon (**eon.chris** e.g.) for each for sensor entities that you're creating.
