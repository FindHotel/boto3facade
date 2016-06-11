boto3facade
=========================

[![Build Status](https://travis-ci.org/FindHotel/boto3facade.svg?branch=master)](https://travis-ci.org/FindHotel/boto3facade)
[![PyPI](https://img.shields.io/pypi/v/boto3facade.svg?style=flat)](https://pypi.python.org/pypi/boto3facade)

A simple facade for [boto3][boto3] that makes some common tasks easier. The 
`boto3facade` module is not intended to be used directly but as a shared
components of projects that use boto3.


[boto3]: https://github.com/boto/boto3


## Installation

To install the development version:

```
    pip install git+https://github.com/FindHotel/boto3facade
```

To install the latest stable release:

```
    pip install boto3facade
```

## Quickstart

The `boto3facade` package contains a collection of modules that implement
facades to different AWS services. For instance the `boto3facade.ec2` module
implements the facade to [AWS EC2 service][ec2]. Each of these modules 
typically contain just one class, named as the corresponding AWS service. E.g.
the `boto3facade.ec2` module contains an `Ec2` class. In some cases, there may
also be public module functions that implement utilities that don't require
access to the [AWS boto3 SDK][boto3]. For instance in the EC2 facade:

[ec2]: https://aws.amazon.com/ec2/

```python
import boto3facade.ec2 as ec2

# Get the name of the role associated to the EC2 instance
if ec2.in_ec2():
    # If this code is running in an EC2 instance
    role_name = ec2.get_instance_profile_role()
else:
    role_name = None
```

Facade methods that actually use `boto3` are always implemented as instance
methods:

```python
from boto3facade.ec2 import Ec2

# Create the facade object
my_ec2_facade = Ec2()

# Get the list of AMIs that have tags matching the provided ones
ami_tags = {'Name': 'niceimage', 'Version', 'latest'}
ami_list = my_ec2_facade.get_ami_by_tag(ami_tags)

# Get the SecurityGroup boto3 resource with a certain name
my_sg = my_ec2_facade.get_sg_by_name('sgname')
```


## Development

```
    make develop
    . .env/bin/activate
```


## Contact

If you have questions, bug reports, suggestions, etc. please create an issue on
the [GitHub project page](http://github.com/FindHotel/boto3facade).


## License

This software is licensed under the [MIT license](http://en.wikipedia.org/wiki/MIT_License)

See [License file](https://github.com/FindHotel/boto3facade/blob/master/LICENSE)


© 2016 German Gomez-Herrero, and FindHotel.
