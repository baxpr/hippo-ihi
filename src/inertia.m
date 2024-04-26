lhV = spm_vol('../INPUTS/case2/lh.hippoAmygLabels-T1.v21.nii.gz');
[lhY,lhXYZ] = spm_read_vols(lhV);

rhV = spm_vol('../INPUTS/case2/rh.hippoAmygLabels-T1.v21.nii.gz');
[rhY,rhXYZ] = spm_read_vols(rhV);

% mm coords of all voxels in both hippocampi
lh_xyz = lhXYZ(:,lhY(:)>0 & lhY(:)<1000);
rh_xyz = rhXYZ(:,rhY(:)>0 & rhY(:)<1000);
xyz = [lh_xyz rh_xyz];

% mm coords relative to center of mass
com = mean(xyz,2);

x = xyz(1,:) - com(1);
y = xyz(2,:) - com(2);
z = xyz(3,:) - com(3);

% Inertia tensor
Ixx = sum(y.^2 + z.^2);
Iyy = sum(x.^2 + z.^2);
Izz = sum(x.^2 + y.^2);

Ixy = -x*y';
Ixz = -x*z';
Iyz = -y*z';

Imat = [ ...
    Ixx Ixy Ixz;
    Ixy Iyy Iyz;
    Ixz Iyz Izz
    ];

% eig produces right-side eigenvectors so that
%   Imat*V = V*D
% First vector is L/R, second is A/P, third is I/S. This is the order such
% that moment of inertia about each axis is in order from lowest to
% highest.
[eigvec,eigval] = eig(Imat);

% There are several coordinate systems in play:
%     - Voxel frame ijk
%     - Lab/world frame, mm from nifti header, xyz = affine * ijk
%     - Inertial frame

% The columns of the eigenvector matrix (i.e. the eigenvectors) are the
% inertial principal axes in the lab frame.
figure(1); clf
subplot(1,2,1); hold on
plot3(x,y,z,'.k')
plot3([0 40*eigvec(1,1)],[0 40*eigvec(2,1)],[0 40*eigvec(3,1)],'-r')
plot3([0 40*eigvec(1,2)],[0 40*eigvec(2,2)],[0 40*eigvec(3,2)],'-g')
plot3([0 40*eigvec(1,3)],[0 40*eigvec(2,3)],[0 40*eigvec(3,3)],'-b')
xlabel('X (lab)')
ylabel('Y (lab)')
zlabel('Z (lab)')
grid on
axis equal


% Pre-multiplying a lab frame coord by eigvec' gives the same coord in the
% inertial frame. To re-orient the hippocampus, we want these inertial
% frame coords for each voxel in the structure.
rxyz = eigvec' * [x; y; z];
rx = rxyz(1,:);
ry = rxyz(2,:);
rz = rxyz(3,:);

figure(1)
subplot(1,2,2); hold on
plot3(rx,ry,rz,'.k')
plot3([0 40],[0 0],[0 0],'-r')
plot3([0 0],[0 40],[0 0],'-g')
plot3([0 0],[0 0],[0 40],'-b')
xlabel('X (inertial)')
ylabel('Y (inertial)')
zlabel('Z (inertial)')
grid on
axis equal


% We should be able to adjust the affine to convert the lab frame coords to
% inertial frame coords
pretrans = [
    1 0 0 -com(1);
    0 1 0 -com(2);
    0 0 1 -com(3);
    0 0 0 1
    ];
rot = [
    eigvec' [0; 0; 0];
    0 0 0 1
    ];
posttrans = [
    1 0 0 com(1);
    0 1 0 com(2);
    0 0 1 com(3);
    0 0 0 1
    ];
lh_newaffine = posttrans * rot * pretrans * lhV.mat;


%%
% Flip signs on principal axes (rows of np_eigvec) to make the largest
% element positive. Eigvec direction is arbitrary and algorithm dependent
for row = 1:3
    [~,idx] = max(abs(np_eigvec(row,:)));
    flip = sign(np_eigvec(row,idx));
    np_eigvec(row,:) = flip * np_eigvec(row,:);
end


%%
% Compare vs numpy.linalg.eig - why do we need to transpose for case2?
% Somehow python is computing a different Imat for case2 (signs opposite on
% off-diags). We have the same number of voxels for python and matlab, min
% and max x,y,z coords of hippo voxels match.
np_eigvec = [ ...
    0.99796191  0.06320797 -0.00876178;
    -0.04870839  0.84324049  0.5353251;
    0.0412251  -0.53380729  0.84460066
    ];


% xyz coords
min(xyz(3,:))
max(xyz(3,:))



figure(3); clf; hold on

plot3(x,y,z,'.k')

plot3([0 40*eigvec(1,1)],[0 40*eigvec(1,2)],[0 40*eigvec(1,3)],'-r')
plot3([0 40*eigvec(2,1)],[0 40*eigvec(2,2)],[0 40*eigvec(2,3)],'-g')
plot3([0 40*eigvec(3,1)],[0 40*eigvec(3,2)],[0 40*eigvec(3,3)],'-b')

plot3([0 40*np_eigvec(1,1)],[0 40*np_eigvec(1,2)],[0 40*np_eigvec(1,3)],'-.r')
plot3([0 40*np_eigvec(2,1)],[0 40*np_eigvec(2,2)],[0 40*np_eigvec(2,3)],'-.g')
plot3([0 40*np_eigvec(3,1)],[0 40*np_eigvec(3,2)],[0 40*np_eigvec(3,3)],'-.b')

xlabel('X (lab)')
ylabel('Y (lab)')
zlabel('Z (lab)')

grid on
axis equal



