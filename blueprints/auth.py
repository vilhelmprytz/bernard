####################################################################
#                                                                  #
# Bernard                                                          #
# Copyright (C) 2020, Vilhelm Prytz, <vilhelm@prytznet.se>, et al. #
#                                                                  #
# Licensed under the terms of the MIT license, see LICENSE.        #
# https://github.com/vilhelmprytz/bernard                          #
#                                                                  #
####################################################################

from flask import Blueprint

auth_blueprint = Blueprint("auth", __name__, template_folder="../templates")
