import rhinoscriptsyntax as rs
import math
##############################
# Dimpled Surface Generator
# Only Spherical Dimples
##############################
D = 60.0 #Dimple Diameter
d = 1.2 #Dimple Depth
r = 1.2 #Fillet Radius
R = (D**2.0/4.0/d+d-2.0*r)/2.0
th = math.asin((D/2.0)/(r+R))
thd = th*(180/math.pi)
dz = r-r*math.cos(th)
nl = 3
dl = 1.0001*D
nw = 4
dw = 1.0001*D
##############################
def is_bbox_inside(bbox1, bbox2):
    for point in bbox1:
        # If any point of bbox1 is outside bbox2, return False
        if (point[0] < bbox2[0][0] or point[0] > bbox2[1][0] or
            point[1] < bbox2[0][1] or point[1] > bbox2[3][1] or
            point[2] < bbox2[0][2] or point[2] > bbox2[4][2]):
            return False
    return True
##############################
# Plane for dimple generation
plane_surface = rs.AddPlaneSurface(rs.WorldXYPlane(), dl, dw)
rs.MoveObject(plane_surface,[-dl,0,-dz])
# Sphere to split
sphere_center = [-dl/2, dw/2, R-d]
sphere_radius = R
sphere = rs.AddSphere(sphere_center, sphere_radius)
# Split with the plane
split_sphere = rs.SplitBrep(sphere, plane_surface,delete_input=True)
# Delete the plane and upper part of the sphere
if split_sphere:
    for part in split_sphere:
        centroid = rs.SurfaceAreaCentroid(part)[0]
        if centroid[2] >= 0:
            rs.DeleteObject(part)
        elif centroid[2] < 0:
            dimple_down = part
else:
    print("Failed to split the sphere.")
rs.DeleteObject(plane_surface)
# Circle for the fillet
circle = rs.AddCircle(rs.WorldXYPlane(),D/2)
circle = rs.MoveObject(circle,[-dl/2,dw/2,0])
# Draw the arc of fillet
plane = rs.WorldXYPlane()
plane = rs.RotatePlane(plane, 90, plane.XAxis)
plane = rs.RotatePlane(plane, 90, plane.ZAxis)
arc = rs.AddArc(plane,r,-thd)
arc = rs.MoveObject(arc,[-dl/2-D/2,dw/2,-r])
# Sweep for fillet
fillet = rs.AddSweep1(circle,[arc])
dimple = rs.JoinSurfaces([fillet,dimple_down],delete_input=True)
#
rs.DeleteObject(circle)
rs.DeleteObject(arc)
#
length = dl+(nl-1)*dl*math.cos(math.pi/6)
width = nw*dw
plane_surface = rs.AddPlaneSurface(rs.WorldXYPlane(), length, width)

for i in range(0,nw):
    for j in range(1,nl+1):
        if (j%2) == 1:
            new_dimple = rs.CopyObject(dimple,[dl+dl*math.cos(math.pi/6)*(j-1),dw*i,0])
            split_plane = rs.SplitBrep(plane_surface,new_dimple,delete_input=True)
            sphere_bbox = rs.BoundingBox(new_dimple)
            if split_plane:
                # Step 6: Delete the circular part of the plane inside the sphere's bounding box
                for part in split_plane:
                    # Get the bounding box of each part of the plane
                    plane_part_bbox = rs.BoundingBox(part)
                    # Check if the plane part's bounding box is inside the sphere's bounding box
                    if is_bbox_inside(plane_part_bbox, sphere_bbox) is True:
                        rs.DeleteObject(part)  # Delete the circular part inside the sphere
                        print("Plane split and circular part deleted successfully.")
                    elif is_bbox_inside(plane_part_bbox, sphere_bbox) is False:
                        plane_surface = part
        elif (j%2) == 0:
            if i < nw-1:
                new_dimple = rs.CopyObject(dimple,[dl+dl*math.cos(math.pi/6)*(j-1),dw*i+0.5*dw,0])
                split_plane = rs.SplitBrep(plane_surface,new_dimple,delete_input=True)
                sphere_bbox = rs.BoundingBox(new_dimple)
                if split_plane:
                    # Step 6: Delete the circular part of the plane inside the sphere's bounding box
                    for part in split_plane:
                        # Get the bounding box of each part of the plane
                        plane_part_bbox = rs.BoundingBox(part)
                        # Check if the plane part's bounding box is inside the sphere's bounding box
                        if is_bbox_inside(plane_part_bbox, sphere_bbox) is True:
                            rs.DeleteObject(part)  # Delete the circular part inside the sphere
                            print("Plane split and circular part deleted successfully.")
                        elif is_bbox_inside(plane_part_bbox, sphere_bbox) is False:
                            plane_surface = part
#Delete the first dimple
rs.DeleteObject(dimple)
