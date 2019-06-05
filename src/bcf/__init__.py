import os

bcfDir = os.path.dirname(__file__)
srcDir = os.path.abspath(os.path.join(bcfDir, os.pardir))
interfacesDir = os.path.join(srcDir, "interfaces")
__path__.append(bcfDir)
__path__.append(interfacesDir)
__all__ = ["reader", "writer"]

