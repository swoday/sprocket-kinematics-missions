% Ready for Task 02: Sprocket.urdf imported as the Simscape Multibody model Sprocket.
if ~exist("urdfFile", "var") || ~isfile(urdfFile)
    setup_sprocket_high_five
end
mdl = "Sprocket";
if ~bdIsLoaded(char(mdl))
    smimport(urdfFile, "ModelName", mdl);
end
