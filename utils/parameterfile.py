### Import standard modules
import json
from pathlib import Path

### Import external modules
import yaml

### Import personal modules
from utils.filename import FileName
from utils.coloredlog import ColorLogger, get_logger, LOGLEVEL_SUCCESS, LOGLEVEL_DISABLE
   
### Retrieve Json or Yaml Content
class ParameterFile():
    def __init__(self, filename:Path="", logger:ColorLogger=None):
        self.filename = FileName()
        self.parameters={}
        self.logger = ColorLogger()
        if logger is None:
            self.logger = get_logger(logger_name="ParameterFile", console_loglevel=LOGLEVEL_DISABLE)
        else:
            self.logger = logger
        if filename:
            self.filename = FileName(filename)
            self.load()
        
    def load(self) -> dict:
        """Return a Dictionnary from Json or Yaml file

        Args:
            filename (file): File Name containing settings. Supported format : Json or Yaml

        Returns:
            Dictionnary: [A Dictionnary build from Json/YAML]
        """
        self.parameters = {}
        filetype = self.filename.fileextension.lower()

        supported_filetype = [".json", ".yaml", ".yml"]
        if filetype not in supported_filetype:
            self.logger.error(f"Parameter file supports following format only: json, yml, yaml.")
        else:
            try:
                if filetype == ".json":
                    with open(self.filename.fullpath) as config_file:
                        self.parameters = json.load(config_file)
                elif filetype == ".yaml" or filetype == ".yml" :
                    with open(self.filename.fullpath) as config_file:
                        self.parameters = yaml.safe_load(config_file)
            except Exception as e:
                self.logger.error(f"with Parameter File '{self.filename.fullpath}':")
                self.logger.error(f"{str(e)}")
            else:
                self.logger.log(LOGLEVEL_SUCCESS, f"Parameter file '{self.filename.fullpath}' successfuly loaded")

        return self.parameters

if __name__ == "__main__":
    import os
    CUR_DIR=os.path.dirname(os.path.abspath(__file__))
    APPNAME, _ = os.path.splitext(os.path.basename(__file__))
    LOG_DIR=os.path.join(CUR_DIR,"../log")
    LOGFILE = None      # os.path.join(LOG_DIR,APPNAME+".log")
    logger = get_logger(logfile=LOGFILE)

    paramfile = os.path.join(CUR_DIR,"../data/sample.yaml")
    param_object =ParameterFile(filename=paramfile, logger=logger)
    print("*** Content of parameter file:")
    print(param_object.parameters)