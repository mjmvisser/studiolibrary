#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/mutils\namespace.py
import traceback
try:
    import maya.cmds
except ImportError:
    traceback.print_exc()

__all__ = ['setNamespace',
 'getFromDagPath',
 'getFromDagPaths',
 'getFromSelection']

def setNamespace(dagPath, namespace):
    """
    Return the given dagPath with the given namespace.
    
    setNamespace("|group|control", "character")
    result: |character:group|character:control
    
    setNamespace("|character:group|character:control", "")
    result: |group|control
    
    :type namespace: str
    """
    result = dagPath
    currentNamespace = getFromDagPath(dagPath)
    if namespace == currentNamespace:
        pass
    elif currentNamespace and namespace:
        result = dagPath.replace(currentNamespace + ':', namespace + ':')
    elif currentNamespace and not namespace:
        result = dagPath.replace(currentNamespace + ':', '')
    elif not currentNamespace and namespace:
        result = dagPath.replace('|', '|' + namespace + ':')
        if namespace and not result.startswith('|'):
            result = namespace + ':' + result
    return result


def getFromDagPaths(dagPaths):
    """
    :type dagPaths: list[str]
    :rtype: list[str]
    """
    namespaces = []
    for dagPath in dagPaths:
        namespace = getFromDagPath(dagPath)
        namespaces.append(namespace)

    return list(set(namespaces))


def getFromDagPath(dagPath):
    """
    :type dagPath: str
    :rtype: str
    """
    shortName = dagPath.split('|')[-1]
    namespace = ':'.join(shortName.split(':')[:-1])
    return namespace


def getFromSelection():
    """
    :rtype: list[str]
    """
    dagPaths = maya.cmds.ls(selection=True)
    return getFromDagPaths(dagPaths)
