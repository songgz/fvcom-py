"""
Tools for manipulating and converting unstructured grids in a range of formats.

"""

import matplotlib.pyplot as plt
import numpy as np
import math

def parseUnstructuredGridSMS(mesh):
    """
    Reads in the SMS unstructured grid format. Also creates IDs for output to
    MIKE unstructured grid format.

    Parameters
    ----------

    mesh : str
        Full path to an SMS unstructured grid (.2dm) file.

    Returns
    -------

    triangle : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    nodes : ndarray
        Integer number assigned to each node.
    X, Y, Z : ndarray
        Coordinates of each grid node and any associated Z value.
    types : ndarray
        Classification for each node string based on the number of node
        strings + 2. This is mainly for use if converting from SMS .2dm
        grid format to DHI MIKE21 .mesh format since the latter requires
        unique IDs for each boundary (with 0 and 1 reserved for land and
        sea nodes).

    """

    fileRead = open(mesh, 'r')
    lines = fileRead.readlines()
    fileRead.close()

    triangles = []
    nodes = []
    types = []
    nodeStrings = []
    x = []
    y = []
    z = []

    # MIKE unstructured grids allocate their boundaries with a type ID flag.
    # Although this function is not necessarily always the precursor to writing
    # a MIKE unstructured grid, we can create IDs based on the number of node
    # strings in the SMS grid. MIKE starts counting open boundaries from 2 (1
    # and 0 are land and sea nodes, respectively).
    typeCount = 2

    for line in lines:
        line = line.strip()
        if line.startswith('E3T'):
            ttt = line.split()
            t1 = int(ttt[2])-1
            t2 = int(ttt[3])-1
            t3 = int(ttt[4])-1
            triangles.append([t1, t2, t3])
        elif line.startswith('ND '):
            xy = line.split()
            x.append(float(xy[2]))
            y.append(float(xy[3]))
            z.append(float(xy[4]))
            nodes.append(int(xy[1]))
            # Although MIKE keeps zero and one reserved for normal nodes and
            # land nodes, SMS doesn't. This means it's not straightforward
            # to determine this information from the SMS file alone. It woud
            # require finding nodes which are edge nodes and assigning their
            # ID to one. All other nodes would be zero until they were
            # overwritten when examining the node strings below.
            types.append(0)
        elif line.startswith('NS '):
            allTypes = line.split(' ')

            for nodeID in allTypes[2:]:
                types[np.abs(int(nodeID))-1] = typeCount
                nodeStrings.append(int(nodeID))

                # Count the number of node strings, and output that to types.
                # Nodes in the node strings are stored in nodeStrings.
                if int(nodeID) < 0:
                    typeCount+=1


    # Convert to numpy arrays.
    triangle = np.asarray(triangles)
    nodes = np.asarray(nodes)
    types = np.asarray(types)
    X = np.asarray(x)
    Y = np.asarray(y)
    Z = np.asarray(z)

    return triangle, nodes, X, Y, Z, types


def parseUnstructuredGridFVCOM(mesh):
    """
    Reads in the FVCOM unstructured grid format.

    Parameters
    ----------

    mesh : str
        Full path to the FVCOM unstructured grid file (.dat usually).

    Returns
    -------

    triangle : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    nodes : ndarray
        Integer number assigned to each node.
    X, Y, Z : ndarray
        Coordinates of each grid node and any associated Z value.

    """

    fileRead = open(mesh, 'r')
    # Skip the file header (two lines)
    lines = fileRead.readlines()[2:]
    fileRead.close()

    triangles = []
    nodes = []
    x = []
    y = []
    z = []

    for line in lines:
        ttt = line.strip().split()
        if len(ttt) == 5:
            t1 = int(ttt[1])-1
            t2 = int(ttt[2])-1
            t3 = int(ttt[3])-1
            triangles.append([t1, t2, t3])
        elif len(ttt) == 4:
            x.append(float(ttt[1]))
            y.append(float(ttt[2]))
            z.append(float(ttt[3]))
            nodes.append(int(ttt[0]))

    # Convert to numpy arrays.
    triangle = np.asarray(triangles)
    nodes = np.asarray(nodes)
    X = np.asarray(x)
    Y = np.asarray(y)
    Z = np.asarray(z)

    return triangle, nodes, X, Y, Z


def parseUnstructuredGridMIKE(mesh, flipZ=True):
    """
    Reads in the MIKE unstructured grid format.

    Depth sign is typically reversed (i.e. z*-1) but can be disabled by
    passing flipZ=False.

    Parameters
    ----------

    mesh : str
        Full path to the DHI MIKE21 unstructured grid file (.mesh usually).
    flipZ : bool, optional
        DHI MIKE21 unstructured grids store the z value as positive down
        whereas FVCOM wants negative down. The conversion is
        automatically applied unless flipZ is set to False.

    Returns
    -------

    triangle : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    nodes : ndarray
        Integer number assigned to each node.
    X, Y, Z : ndarray
        Coordinates of each grid node and any associated Z value.
    types : ndarray
        Classification for each open boundary. DHI MIKE21 .mesh format
        requires unique IDs for each open boundary (with 0 and 1
        reserved for land and sea nodes).

    """

    fileRead = open(mesh, 'r')
    # Skip the file header (one line)
    lines = fileRead.readlines()[1:]
    fileRead.close()

    triangles = []
    nodes = []
    types = []
    x = []
    y = []
    z = []

    for line in lines:
        ttt = line.strip().split()
        if len(ttt) == 4:
            t1 = int(ttt[1])-1
            t2 = int(ttt[2])-1
            t3 = int(ttt[3])-1
            triangles.append([t1, t2, t3])
        elif len(ttt) == 5:
            x.append(float(ttt[1]))
            y.append(float(ttt[2]))
            z.append(float(ttt[3]))
            types.append(int(ttt[4]))
            nodes.append(int(ttt[0]))

    # Convert to numpy arrays.
    triangle = np.asarray(triangles)
    nodes = np.asarray(nodes)
    types = np.asarray(types)
    X = np.asarray(x)
    Y = np.asarray(y)
    # N.B. Depths should be negative for FVCOM
    if flipZ:
        Z = -np.asarray(z)
    else:
        Z = np.asarray(z)

    return triangle, nodes, X, Y, Z, types


def writeUnstructuredGridSMS(triangles, nodes, x, y, z, types, mesh):
    """
    Takes appropriate triangle, node, boundary type and coordinate data and
    writes out an SMS formatted grid file (mesh). The footer is largely static,
    but the elements, nodes and node strings are parsed from the input data.

    Input data is probably best obtained from one of:

        grid_tools.parseUnstructuredGridSMS()
        grid_tools.parseUnstructuredGridFVCOM()
        grid_tools.parseUnstructuredGridMIKE()

    which read in the relevant grids and output the required information for
    this function.

    The footer contains meta data and additional information. See page 18 in
    http://smstutorials-11.0.aquaveo.com/SMS_Gen2DM.pdf.

    In essence, four bits are critical:
        1. The header/footer MESH2D/BEGPARAMDEF
        2. E3T prefix for the connectivity:
            (elementID, node1, node2, node3, material_type)
        3. ND prefix for the node information:
            (nodeID, x, y, z)
        4. NS prefix for the node strings which indicate the open boundaries.

    As far as I can tell, the footer is largely irrelevant for FVCOM purposes.

    Parameters
    ----------

    triangles : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    nodes : ndarray
        Integer number assigned to each node.
    x, y, z : ndarray
        Coordinates of each grid node and any associated Z value.
    types : ndarray
        Classification for each open boundary. DHI MIKE21 .mesh format
        requires unique IDs for each open boundary (with 0 and 1
        reserved for land and sea nodes). Similar values can be used in
        SMS grid files too.
    mesh : str
        Full path to the output file name.

    """

    fileWrite = open(mesh, 'w')
    # Add a header
    fileWrite.write('MESH2D\n')

    # Write out the connectivity table (triangles)
    currentNode = 0
    for line in triangles:

        # Bump the numbers by one to correct for Python indexing from zero
        line = line + 1
        strLine = []
        # Convert the numpy array to a string array
        for value in line:
            strLine.append(str(value))

        currentNode+=1
        # Build the output string for the connectivity table
        output = ['E3T'] + [str(currentNode)] + strLine + ['1']
        output = ' '.join(output)
        #print output

        fileWrite.write(output + '\n')

    # Add the node information (nodes)
    for count, line in enumerate(nodes):

        # Convert the numpy array to a string array
        strLine = str(line)

        # Format output correctly
        output = ['ND'] + \
                [strLine] + \
                ['{:.8e}'.format(x[count])] + \
                ['{:.8e}'.format(y[count])] + \
                ['{:.8e}'.format(z[count])]
        output = ' '.join(output)

        fileWrite.write(output + '\n')

    # Convert MIKE boundary types to node strings. The format requires a prefix
    # NS, and then a maximum of 10 node IDs per line. The node string tail is
    # indicated by a negative node ID.

    # Iterate through the unique boundary types to get a new node string for
    # each boundary type (ignore types of less than 2 which are not open
    # boundaries in MIKE).
    for boundaryType in np.unique(types[types>1]):

        # Find the nodes for the boundary type which are greater than 1 (i.e.
        # not 0 or 1).
        nodeBoundaries = nodes[types==boundaryType]

        nodeStrings = 0
        for counter, node in enumerate(nodeBoundaries):
            if counter+1 == len(nodeBoundaries) and node > 0:
                node = -node

            nodeStrings += 1
            if nodeStrings == 1:
                output = 'NS  {:d} '.format(int(node))
                fileWrite.write(output)
            elif nodeStrings != 0 and nodeStrings < 10:
                output = '{:d} '.format(int(node))
                fileWrite.write(output)
            elif nodeStrings == 10:
                output = '{:d} '.format(int(node))
                fileWrite.write(output + '\n')
                nodeStrings = 0

        # Add a new line at the end of each block. Not sure why the new line
        # above doesn't work...
        fileWrite.write('\n')

    # Add all the blurb at the end of the file.
    #
    # BEGPARAMDEF = Marks end of mesh data/beginning of mesh model definition
    # GM = Mesh name (enclosed in "")
    # SI = use SI units y/n = 1/0
    # DY = Dynamic model y/n = 1/0
    # TU = Time units
    # TD = Dynamic time data (?)
    # NUME = Number of entities available (nodes, node strings, elements)
    # BGPGC = Boundary group parameter group correlation y/n = 1/0
    # BEDISP/BEFONT = Format controls on display of boundary labels.
    # ENDPARAMDEF = End of the mesh model definition
    # BEG2DMBC = Beginning of the model assignments
    # MAT = Material assignment
    # END2DMBC = End of the model assignments
    footer = 'BEGPARAMDEF\n\
GM  "Mesh"\n\
SI  0\n\
DY  0\n\
TU  ""\n\
TD  0  0\n\
NUME  3\n\
BCPGC  0\n\
BEDISP  0 0 0 0 1 0 1 0 0 0 0 1\n\
BEFONT  0 2\n\
BEDISP  1 0 0 0 1 0 1 0 0 0 0 1\n\
BEFONT  1 2\n\
BEDISP  2 0 0 0 1 0 1 0 0 0 0 1\n\
BEFONT  2 2\n\
ENDPARAMDEF\n\
BEG2DMBC\n\
MAT  1 "material 01"\n\
END2DMBC\n'

    fileWrite.write(footer)

    fileWrite.close()


def writeUnstructuredGridSMSBathy(triangles, nodes, z, PTS):
    """
    Writes out the additional bathymetry file sometimes output by SMS. Not sure
    why this is necessary as it's possible to put the depths in the other file,
    but hey ho, it is obviously sometimes necessary.

    Parameters
    ----------

    triangle : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    nodes : ndarray
        Integer number assigned to each node.
    z : ndarray
        Z values at each node location.
    PTS : str
        Full path of the output file name.

    """

    filePTS = open(PTS, 'w')

    # Get some information needed for the metadata side of things
    nodeNumber = len(nodes)
    elementNumber = len(triangles[:,0])

    # Header format (see http://wikis.aquaveo.com/xms/index.php?title=GMS:Data_Set_Files)
    # DATASET = indicates data
    # OBJTYPE = type of object (i.e. mesh 3d, mesh 2d) data is associated with
    # BEGSCL = Start of the scalar data set
    # ND = Number of data values
    # NC = Number of elements
    # NAME = Freeform data set name
    # TS = Time step of the data
    header = 'DATASET\nOBJTYEP = "mesh2d"\nBEGSCL\nND  {:<6d}\nNC  {:<6d}\nNAME "Z_interp"\nTS 0 0\n'.format(int(nodeNumber), int(elementNumber))
    filePTS.write(header)

    # Now just iterate through all the z values. This process assumes the z
    # values are in the same order as the nodes. If they're not, this will
    # make a mess of your data.
    for depth in z:
        filePTS.write('{:.5f}\n'.format(float(depth)))

    # Close the file with the footer
    filePTS.write('ENDDS\n')
    filePTS.close()


def writeUnstructuredGridMIKE(triangles, nodes, x, y, z, types, mesh):
    """
    Write out a DHI MIKE unstructured grid (mesh) format file. This
    assumes the input coordinates are in longitude and latitude. If they
    are not, the header will need to be modified with the appropriate
    string (which is complicated and of which I don't have a full list).

    If types is empty, then zeros will be written out for all nodes.

    Parameters
    ----------

    triangles : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    nodes : ndarray
        Integer number assigned to each node.
    x, y, z : ndarray
        Coordinates of each grid node and any associated Z value.
    types : ndarray
        Classification for each open boundary. DHI MIKE21 .mesh format
        requires unique IDs for each open boundary (with 0 and 1
        reserved for land and sea nodes).
    mesh : str
        Full path to the output mesh file.

    """
    fileWrite = open(mesh, 'w')
    # Add a header
    output = '{}  LONG/LAT'.format(int(len(nodes)))
    fileWrite.write(output + '\n')

    if len(types) == 0:
        types = np.zeros(shape=(len(nodes),1))

    # Write out the node information
    for count, line in enumerate(nodes):

        # Convert the numpy array to a string array
        strLine = str(line)

        output = \
            [strLine] + \
            ['{}'.format(x[count])] + \
            ['{}'.format(y[count])] + \
            ['{}'.format(z[count])] + \
            ['{}'.format(int(types[count]))]
        output = ' '.join(output)

        fileWrite.write(output + '\n')

    # Now for the connectivity

    # Little header. No idea what the 3 and 21 are all about (version perhaps?)
    #output = '{} {} {}'.format(int(len(triangles)), int(len(np.unique(types))), '21')
    output = '{} {} {}'.format(int(len(triangles)), '3', '21')
    fileWrite.write(output + '\n')

    for count, line in enumerate(triangles):

        # Bump the numbers by one to correct for Python indexing from zero
        line = line + 1
        strLine = []
        # Convert the numpy array to a string array
        for value in line:
            strLine.append(str(value))

        # Build the output string for the connectivity table
        output = [str(count+1)] + strLine
        output = ' '.join(output)

        fileWrite.write(output + '\n')

    fileWrite.close()


def plotUnstructuredGrid(triangles, nodes, x, y, z, colourLabel, addText=False, addMesh=False):
    """
    Takes the output of parseUnstructuredGridFVCOM() or
    parseUnstructuredGridSMS() and readFVCOM() and plots it.

    Parameters
    ----------

    triangles : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    nodes : ndarray
        Integer number assigned to each node.
    x, y, z : ndarray
        Coordinates of each grid node and any associated Z value.
    colourLabel : str
        String to add to the colour bar label.
    addText : bool, optional
        If True, add each node number to the plot.
    addMesh : bool, optional
        If True, overlay the grid mesh on the plot.

    """

    plt.figure()
    if z.max()-z.min() != 0:
        plt.tripcolor(x, y, triangles, z, shading='interp')
        cb = plt.colorbar()
        cb.set_label(colourLabel)

    if addMesh:
        plt.triplot(x, y, triangles, '-', color=[0.6, 0.6, 0.6])

    # Add the node numbers (this is slow)
    if addText:
        for node in nodes:
            plt.text(x[node-1], y[node-1], str(nodes[node-1]),
                horizontalalignment='center', verticalalignment='top', size=8)
    #plt.axes().set_aspect('equal')
    plt.axes().autoscale(tight=True)
    #plt.axis('tight')
    #plt.clim(-500, 0)
    #plt.title('Triplot of user-specified triangulation')
    #plt.xlabel('Metres')
    #plt.ylabel('Metres')

    plt.show()
    #plt.close() # for 'looping' (slowly)


def plotUnstructuredGridProjected(triangles, nodes, x, y, z, colourLabel, addText=False, addMesh=False, extents=False):
    """
    Takes the output of parseUnstructuredGridFVCOM() or
    parseUnstructuredGridSMS() and readFVCOM() and plots it on a projected
    map. Best used for lat-long data sets.

    Give triangles, nodes, x, y, z and a label for the colour scale. The first
    five arguments are the output of parseUnstructuredGridFVCOM() or
    parseUnstructuredGridSMS(). Optionally append addText=True|False and
    addMesh=True|False to enable/disable node numbers and grid overlays,
    respectively. Finally, provide optional extents (W/E/S/N format).

    WARNING: THIS DOESN'T WORK ON FEDORA 14. REQUIRES FEDORA 16 AT LEAST
    (I THINK -- DIFFICULT TO VERIFY WITHOUT ACCESS TO A NEWER VERSION OF
    FEDORA).

    """

    from mpl_toolkits.basemap import Basemap
    from matplotlib import tri

    if extents is False:
        # We don't have a specific region defined, so use minmax of x and y.
        extents = [ min(x), max(x), min(y), max(y) ]

    # Create a triangulation object from the triagulated info read in from the
    # grid files.
    triang = tri.Triangulation(x, y, triangles)

    # Create the basemap
    fig = plt.figure()
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    m = Basemap(
            llcrnrlat=extents[2],
            urcrnrlat=extents[3],
            llcrnrlon=extents[0],
            urcrnrlon=extents[1],
            projection='merc',
            resolution='h',
            lat_1=extents[2],
            lat_2=extents[3],
            lat_0=(extents[3]-extents[2])/2,
            lon_0=extents[1],
            ax=ax)
    # Add the data
    #m.tripcolor(triang,z) # version of matplotlib is too old on Fedora 14
    # Add a coastline
    #m.drawlsmask(land_color='grey', lakes=True, resolution='h')
    # Can't add resolution here for some reason
    #m.drawlsmask(land_color='grey')
    m.drawcoastlines()
    plt.show()


def findNearestPoint(FX, FY, x, y, maxDistance=np.inf, noisy=False):
    """
    Given some point(s) x and y, find the nearest grid node in FX and
    FY.

    Returns the nearest coordinate(s), distance(s) from the point(s) and
    the index in the respective array(s).

    Optionally specify a maximum distance (in the same units as the
    input) to only return grid positions which are within that distance.
    This means if your point lies outside the grid, for example, you can
    use maxDistance to filter it out. Positions and indices which cannot
    be found within maxDistance are returned as NaN; distance is always
    returned, even if the maxDistance threshold has been exceeded.

    Parameters
    ----------

    FX, FY : ndarray
        Coordinates within which to search for the nearest point given
        in x and y.
    x, y : ndarray
        List of coordinates to find the closest value in FX and FY.
        Upper threshold of distance is given by maxDistance (see below).
    maxDistance : float, optional
        Unless given, there is no upper limit on the distance away from
        the source for which a result is deemed valid. Any other value
        specified here limits the upper threshold.
    noisy : bool, optional
        Set to True to enable verbose output.

    Returns
    -------

    nearestX, nearestY : ndarray
        Coordinates from FX and FY which are within maxDistance (if
        given) and closest to the corresponding point in x and y.
    distance : ndarray
        Distance between each point in x and y and the closest value in
        FX and FY. Even if maxDistance is given (and exceeded), the
        distance is reported here.
    index : ndarray
        List of indices of FX and FY for the closest positions to those
        given in x, y.

    """

    if np.ndim(x) != np.ndim(y):
        raise Exception('Number of points in X and Y do not match')

    nearestX = np.empty(np.shape(x))
    nearestY = np.empty(np.shape(x))
    index = np.empty(np.shape(x))
    distance = np.empty(np.shape(x))

    # Make all values NaN
    nearestX = nearestX.ravel() * np.NaN
    nearestY = nearestY.ravel() * np.NaN
    index = index.ravel() * np.NaN
    distance = distance.ravel() * np.NaN

    if np.ndim(x) == 0:
        todo = np.column_stack([x, y])
    else:
        todo = zip(x, y)

    for cnt, pointXY in enumerate(todo):
        if noisy:
            if np.ndim(x) == 0:
                print 'Point {} of {}'.format(cnt + 1, 1)
            else:
                print 'Point {} of {}'.format(cnt + 1, np.shape(x)[0])

        findX, findY = FX - pointXY[0], FY - pointXY[1]
        vectorDistances = np.sqrt(findX**2 + findY**2)
        if np.min(vectorDistances) > maxDistance:
            distance[cnt] = np.min(vectorDistances)
            # Should be NaN already, but no harm in being thorough
            index[cnt], nearestX[cnt], nearestY[cnt] = np.NaN, np.NaN, np.NaN
        else:
            distance[cnt] = np.min(vectorDistances)
            index[cnt] = vectorDistances.argmin()
            nearestX[cnt] = FX[index[cnt]]
            nearestY[cnt] = FY[index[cnt]]

    return nearestX, nearestY, distance, index


def elementSideLengths(triangles, x, y):
    """
    Given a list of triangle nodes, calculate the length of each side of each
    triangle and return as an array of lengths. Units are in the original input
    units (no conversion from lat/long to metres, for example).

    The arrays triangles, x and y can be created by running
    parseUnstructuredGridSMS(), parseUnstructuredGridFVCOM() or
    parseUnstructuredGridMIKE() on a given SMS, FVCOM or MIKE grid file.

    Parameters
    ----------

    triangles : ndarray
        Integer array of shape (ntri, 3). Each triangle is composed of
        three points and this contains the three node numbers (stored in
        nodes) which refer to the coordinates in X and Y (see below).
    x, y : ndarray
        Coordinates of each grid node.

    Returns
    -------

    elemSides : ndarray
        Length of each element described by triangles and x, y.

    """

    elemSides = np.zeros([np.shape(triangles)[0], 3])
    for it, tri in enumerate(triangles):
        pos1x, pos2x, pos3x = x[tri]
        pos1y, pos2y, pos3y = y[tri]

        elemSides[it,0] = sqrt((pos1x - pos2x)**2 + (pos1y - pos2y)**2)
        elemSides[it,1] = sqrt((pos2x - pos3x)**2 + (pos2y - pos3y)**2)
        elemSides[it,2] = sqrt((pos3x - pos1x)**2 + (pos3y - pos1y)**2)

    return elemSides


def fixCoordinates(FVCOM, UTMZone, inVars=['x', 'y']):
    """
    Use the UTMtoLL function to convert the grid from UTM to Lat/Long.
    Returns longitude and latitude in the range -180 to 180.

    By default, the variables which will be converted from UTM to
    Lat/Long are 'x' and 'y'. To specify a different pair, give
    inVars=['xc', 'yc'], for example, to convert the 'xc' and 'yc'
    variables instead. Their order should be x-direction followed by
    y-direction.

    Parameters
    ----------

    FVCOM : dict
        Dict of the FVCOM model results (see
        read_FVCOM_results.readFVCOM).
    UTMZone : str
        UTM Zone (e.g. '30N').
    inVars : list, optional
        List of strings specifying the keys for FVCOM to be used as
        input. Defaults to ['x', 'y'] but if you wanted to convert
        element centres, change to ['xc', 'yc'] instead.

    Returns
    -------

    X, Y : ndarray
        Converted coordinates in longitude and latitude.

    """

    try:
        from ll2utm import UTMtoLL
    except ImportError:
        print('Failed to import ll2utm (available from http://robotics.ai.uiuc.edu/~hyoon24/LatLongUTMconversion.py')

    try:
        Y = np.zeros(np.shape(FVCOM[inVars[1]])) * np.nan
        X = np.zeros(np.shape(FVCOM[inVars[0]])) * np.nan
    except IOError:
        print 'Couldn''t find the {} or {} variables in the supplied FVCOM dict. Check you loaded them and try again.'.format(inVars[0], inVars[1])

    for count, posXY in enumerate(zip(FVCOM[inVars[0]], FVCOM[inVars[1]])):

        posX = posXY[0]
        posY = posXY[1]

        # 23 is the WGS84 ellipsoid
        tmpLat, tmpLon = UTMtoLL(23, posY, posX, UTMZone)

        Y[count] = tmpLat
        X[count] = tmpLon

    # Make the range -180 to 180 rather than 0 to 360.
    if np.min(X) >= 0:
        X[X > 180] = X[X > 180] - 360

    return X, Y


def plotCoast(coastline):
    """
    Take an ESRI shapefile and output the paths required by
    matplotlib.patches.  This is until I get the new version of
    matplotlib which does Basemap with unstructured grids.

    Parameters
    ----------

    coastline : str
        Full path to an ESRI ShapeFile of a coastline.

    Returns
    -------

    paths : list
        List of matplotlib.path.Paths which can be used with
        matplotlib.patches.PathPatch to plot the ShapeFile.

    Notes
    -----

    Lifted from:
    http://ondrejintheair.blogspot.co.uk/2011/11/plot-polygon-shapefiles-using-ogr-and.html

    """

    import numpy as np
    import matplotlib.path as mpath
    from osgeo import ogr

    # Load in a coastline shape file
    ds = ogr.Open(coastline)
    lyr = ds.GetLayer(0)
    ext = lyr.GetExtent()

    paths = []
    lyr.ResetReading()

    # Read all features in layer and store as paths
    for feat in lyr:
        geom = feat.GetGeometryRef()
        # check if geom is polygon
        if geom.GetGeometryType() == ogr.wkbPolygon:
            codes = []
            all_x = []
            all_y = []
            for i in xrange(geom.GetGeometryCount()):
                # Read ring geometry and create path
                r = geom.GetGeometryRef(i)
                x = [r.GetX(j) for j in range(r.GetPointCount())]
                y = [r.GetY(j) for j in range(r.GetPointCount())]
                # skip boundary between individual rings
                codes += [mpath.Path.MOVETO] + (len(x)-1)*[mpath.Path.LINETO]
                all_x += x
                all_y += y
            path = mpath.Path(np.column_stack((all_x,all_y)), codes)
            paths.append(path)

    return paths


def clipTri(MODEL, sideLength, keys=['xc', 'yc']):
    """
    Make a new triangulation of the element centres and clip according
    to a maximum length.

    Parameters
    ----------

    MODEL : dict
        Contains the MODEL model results. Keys are those specified in
        getVars.
    sideLength : float
        Maximum length of an element before it is clipped.
    keys : list, optional
        List of two keys to use as the x and y coordinates for the
        triangulation. Defaults to ['xc', 'yc'].

    Returns
    -------

    triClip : ndarray
        Triangulation (indices of the coordinates which make up an
        element) of the new clipped elements. This can be used with the
        input coordinates in MODEL to plot the new unstructured grid.

    """

    import matplotlib.delaunay as triang

    cens, edg, tri, neig = triang.delaunay(MODEL[keys[0]], MODEL[keys[1]])

    # Get the length of all element edges
    xx, yy = MODEL[keys[0]][tri], MODEL[keys[1]][tri]
    dx = np.empty(np.shape(xx))
    dy = np.empty(np.shape(yy))
    sxy = np.empty(np.shape(xx))
    dx[:,0] = xx[:,0] - xx[:,1]
    dx[:,1] = xx[:,1] - xx[:,2]
    dx[:,2] = xx[:,2] - xx[:,0]
    dy[:,0] = yy[:,0] - yy[:,1]
    dy[:,1] = yy[:,1] - yy[:,2]
    dy[:,2] = yy[:,2] - yy[:,0]
    sxy[:,0] = np.sqrt(dx[:,0]**2 + dy[:,1]**2)
    sxy[:,1] = np.sqrt(dx[:,1]**2 + dy[:,2]**2)
    sxy[:,2] = np.sqrt(dx[:,2]**2 + dy[:,0]**2)

    triClip = []
    for i, t in enumerate(sxy):
        if max(t) <= sideLength:
            # Keep this element
            triClip.append(tri[i])

    triClip = np.asarray(triClip)

    return triClip
