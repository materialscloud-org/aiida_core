import os, os.path
import shutil
import fnmatch

class Folder(object):
    """s
    A class to manage generic folders, avoiding to get out of specific given folder borders.
    
    .. todo:: fix this, os.path.commonprefix of /a/b/c and /a/b2/c will give
        a/b, check if this is wanted or if we want to put trailing slashes.
        (or if we want to use os.path.relpath and check for a string starting
        with os.pardir?)
    """
    def __init__(self, abspath, folder_limit=None):
        abspath = os.path.realpath(abspath)
        if folder_limit is None:
            folder_limit = abspath
        folder_limit = os.path.realpath(folder_limit)

        # check that it is a subfolder
        if not os.path.commonprefix([abspath,folder_limit]) == folder_limit:
            raise ValueError("The absolute path for this folder is not within the folder_limit. "
                             "abspath={}, folder_limit={}.".format(abspath, folder_limit))

        self._abspath = os.path.realpath(abspath)
        self._folder_limit = folder_limit

    
    def get_subfolder(self, subfolder, create=False):
        """
        Return a Folder object pointing to a subfolder.

        Args:
            subfolder: a string with the relative path of the subfolder,
                relative to the absolute path of this object. Note that
                this may also contain '..' parts,
                as far as this does not go beyond the folder_limit.
            create: if True, the new subfolder is created, if it does not exist.
            
        Returns:
            a Folder object pointing to the subfolder.
            The subfolder limit will be the same of the parent.
        """
        dest_abs_dir = os.path.realpath(os.path.join(
                self.abspath,unicode(subfolder)))

        # Create a new Folder object, with the same limit of the parent
        new_folder = Folder(abspath=dest_abs_dir, 
                            folder_limit = self.folder_limit)
        
        if create:
            new_folder.create()
            
        return new_folder
    
    def get_content_list(self,pattern='*'):
        """
        Return a list of files (and subfolders) in the folder,
        matching a given pattern.

        Example: If you want to exclude files starting with a dot, you can
        call this method with pattern='[!.]*'

        Args:
            pattern: a pattern for the file/folder names, using Unix filename
                pattern matching (see Python standard module fnmatch).
                By default, pattern is '*', matching all files and folders.
        Returns:
            a list of tuples of two elements, the first is the file name and
            the second is True if the element is a file, False if it is a
            directory.
        """
        return [(fname,not os.path.isdir(os.path.join(self.abspath, fname))) 
                for fname in os.listdir(self.abspath)
                if fnmatch.fnmatch(fname, pattern)]

    def create_symlink(self, src, name):
        """
        Create a symlink inside the folder to the location 'src'.

        Args:
            src: the location to which the symlink must point. Can be
                either a relative or an absolute path. Should, however, 
                be relative to work properly also when the repository is
                moved!
            name: the filename of the symlink to be created.
        """
        dest_abs_path = self.get_filename(name)
        os.symlink(src,dest_abs_path)

    def insert_file(self,src,dest_name=None):
        """
        Copy a file to the folder.
        
        Args:
            src: the source filename to copy
            dest_name: if None, the same basename of src is used. Otherwise,
                the destination filename will have this file name.
        """
        if dest_name is None:
            filename = unicode(os.path.basename(src))
        else:
            filename = unicode(dest_name)

        # I get the full path of the filename, checking also that I don't
        # go beyond the folder limits
        dest_abs_path = self.get_filename(filename)

        shutil.copyfile(src,dest_abs_path)
        return dest_abs_path

    def get_filename(self,filename):
        """
        Return an absolute path for a filename in this folder.
        
        The advantage of using this method is that it checks that filename is a valid
        filename within this folder, and not something e.g. containing slashes.
        
        Args:
            filename: The filename to open.
        """
        dest_abs_path = os.path.join(self.abspath,filename)
        
        if not os.path.split(dest_abs_path) == (self.abspath,filename):
            errstr = "You didn't specify a valid filename: {}".format(filename)
            raise ValueError(errstr)

        return dest_abs_path


    @property
    def abspath(self):
        """
        The absolute path of the folder.
        """
        return self._abspath


    @property
    def folder_limit(self):
        """
        The folder limit that cannot be crossed when creating files and folders.
        """
        return self._folder_limit


    def exists(self):
        """
        Return True if the folder exists, False otherwise.
        """
        return os.path.exists(self.abspath)


    def erase(self,create_empty_folder=False):
        """
        Erases the folder. Should be called only in very specific cases,
        in general folder should not be erased!

        Doesn't complain if the folder does not exist.

        Args:
            create_empty_folder: if True, after erasing, creates an empty dir.
        """
        if self.exists():
            shutil.rmtree(self.abspath)

        if create_empty_folder:
            self.create()


    def create(self):
        """
        Creates the folder, if it does not exist on the disk yet.

        It will also create top directories, if absent.

        It is always safe to call it, it will do nothing if the folder
        already exists.
        """
        if not self.exists():
            os.makedirs(self.abspath)


    def replace_with_folder(self, srcdir, move=False, overwrite=False):
        """
        This routine copies or moves the source folder 'srcdir' to the local
        folder pointed by this Folder object.
        
        Args:
            srcdir: the source folder on the disk
            move: if True, the srcdir is moved to the repository. Otherwise, it
                is only copied.
            overwrite: if True, the folder will be erased first.
                if False, a IOError is raised if the folder already exists.
                Whatever the value of this flag, parent directories will be
                created, if needed.

        Raises:
            OSError or IOError: in case of problems accessing or writing
                the files.
            ValueError: if the section is not recognized.
        """
        if overwrite:
            self.erase()
        elif self.exists():
            raise IOError("Location {} already exists, and overwrite is set to "
                          "False".format(self.abspath))

        # Create parent dir, if needed
        pardir = os.path.dirname(self.abspath)
        if not os.path.exists(pardir):
            os.makedirs(pardir)

        if move:
            shutil.move(srcdir,self.abspath)
        else:
            shutil.copytree(srcdir,self.abspath)


if __name__ == "__main__":
    # .. todo:: implement tests here
    pass