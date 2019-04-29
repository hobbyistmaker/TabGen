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

The options available so far are:

**Fingers Type**: Can be user-defined or automatic.
* User-defined will use the tab width to calculate the number of fingers on the face, and offset the first and last finger from the edges to make sure that all fingers are the same size.
* Automatic will use the tab width to calculate the number of fingers on the face, but size the fingers up or down to make sure that they are all the same size; including the offsets from the edge.

**Placement**: Will allow you to place fingers on one face, or on two faces

**Face**: The face where fingers should be placed. If an edge has already been selected in the next box, then you should only be able to select parallel faces to that edge.

**Duplicate Face**: The edge where the second set of fingers should be placed. This should only allow you to select edges that are parallel to the primary face.

**Tab Width**: The width of the fingers for user-defined tabs, or the target width for automatic tabs. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.

**Material Thickness**: The depth of the tabs cut into the face. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.

**Start with tab**: If enabled, the the edges of the face will have a tab, if disabled, the will start with a cut.

**Make parametric**: If enabled, will define a number of formulas that will be used to automatically change the finger settings when the corresponding length, distance or tab width parameters are changed.

**Length parameter**: The length of the face along which the tabs/cuts will be placed. This value will be initially calculated based on the face selected. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.

**Distance parameter**: The distance from the primary face to the secondary face. This value will be initially calculated based on the face and edge selected. This can be a numeric value, or the name of a user-defined parameter that has already been setup in F360.
