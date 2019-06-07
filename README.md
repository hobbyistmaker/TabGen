# TabGen
Fusion 360 add-in for generating finger-joint tabs

This is a very alpha version of the plugin, and may be prone to strange bugs.

If using the parametric features: You can define the parametric features more efficiently by doing things by hand. This plugin has to create parameters for each face–at the moment–so you will see more parameters defined using it. If you have other user-defined parameters that you want to use, you may have to manually update multiple plugin-defined parameters to get everything in sync. I leave this as an exercise to the reader right now.

### Installation ###

1. Download the ZIP file from github and extract it to a known location.
   * The Fusion360 Add-ins folder is located at "**~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns**” on a Mac.
2. Click on the **Add-Ins** menu from Fusion 360.
3. Select the **Add-Ins tab** from the *Scripts and Add-ins* dialog.
4. Click on the green + next to the *My Add-ins* folder.
5. Find the location where you uncompressed the ZIP file above and **select that directory**.
6. If everything works, you can now select *TabGen* from the *Add-Ins list* and click on **Run** to start it.
7. Now you should see a **Generate Tabs** option underneath the *Add-Ins menu*.

### Options ###

The options available on the Main Tab so far are:

![Image of the Main Tab](resources/Main%20tab.png)

**Fingers Type**: **Automatic Width** or **Constant Width**
* Constant Width will use the tab width to calculate the number of fingers on the face, and offset the first and last finger from the edges to make sure that all fingers are the same size.
* Automatic Width will use the tab width to calculate the number of fingers on the face, but size the fingers up or down to make sure that they are all the same size; including the offsets from the edge.

**Placement**: Will allow you to place fingers on one face, or on two faces

**Face**: The face where fingers should be placed. If an edge has already been selected in the next box, then you should only be able to select parallel faces to that edge.

**Secondary Face**: The face where the second set of fingers should be placed. The plugin will attempt to automatically select the secondary face, when **Dual Edge** placement is enabled, but you can also select a secondary face manually; if, for instance, the two faces are not equal in length.

**Tab Width**: The width of the fingers for user-defined tabs, or the target width for automatic tabs. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.

**Tab Depth**: The depth of the tabs cut into the face. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.

**Start with tab**: If enabled, the the edges of the face will have a tab, if disabled, the will start with a cut.

**Face Length**: The length of the face along which the tabs/cuts will be placed. This value will be initially calculated based on the face selected. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.

**Duplicate Distance**: The distance from the primary face to the secondary face. This value will be initially calculated based on the face and edge selected. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.

**Disable parametric**: If enabled, this will turn off the ability to populate the model parameters with formulas. This will give you slightly better performance in your model, but will make it more difficult to fine tune parameters later.

**Enable Preview**: Will enable preview mode, which will attempt to show you what your body will look like with the given settings.

On the Advanced Tab:

![Image of the Advanced Tab](resources/Advanced%20Tab.png)

**Interior Walls**: This will place notches equally across the **Duplicate Distance**, for situations where you want to have other walls finger jointed in the interior of the body.

**Margins from Sides**: This will prevent any notches from being cut at the sides of the face, within the distance specified.

**Margin from Edge**: This will offset the fingers from the face, allowing for notches to be cut inside the selected body. You can use this feature to place notches at odd offsets in the body, rather than using the Interior Walls function that will space them evenly.

**Kerf Adjustment**: This will adjust the depth and width of the tabs to account for kerf of your machine. The CAM module is the preferred place for adjusting kerf, but this option can be used for situations where you are not using the CAM module.