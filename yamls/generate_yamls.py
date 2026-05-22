template_files = {
    "shear": "TEMPLATE_SHEAR.yaml",
    "3x2": "TEMPLATE_3X2.yaml",
}

def validate_template(template):
    """
        This is an useful function that list all placeholders
    """
    return "%CHAIN_NAME%" in template and \
           "%NON_LINEAR_EMUL%" in template and \
           "%DATASET_FILE%" in template and \
           "%RMINUSONE%" in template and \
           "%RMINUSONE_95CL%" in template and \
           r"%EXTRA_COSMO_PARAMS%" in template

def generate_yaml(probe, chain_name, dataset_file, non_linear_emul=1, rminusone=0.02, rminusone_cl=0.2, extra_cosmo_params=None):
    if probe not in template_files:
        raise Exception(f"Unsupported probe {probe}. Available probes are {list(template_files.keys())}")
    
    template_file = template_files[probe]
    with open(template_file, "r") as f:
        template = f.read()

    assert validate_template(template), "Could not find placeholder fields in template"

    contents = template.replace("%CHAIN_NAME%", chain_name)
    contents = contents.replace("%NON_LINEAR_EMUL%", str(non_linear_emul))
    contents = contents.replace("%DATASET_FILE%", dataset_file)
    contents = contents.replace("%RMINUSONE%", str(rminusone))
    contents = contents.replace("%RMINUSONE_95CL%", str(rminusone_cl))
    if extra_cosmo_params is None:
        contents = contents.replace(r"%EXTRA_COSMO_PARAMS%", "")
    else:
        raise Exception(f"Unsupported extra cosmo params {extra_cosmo_params}")

    with open(f"{chain_name}.yaml", "w") as f:
        f.write(contents)

    if "%" in contents:
        raise Exception("Some placeholder was not substituted!")

    print(f"Generated {chain_name}.yaml")

generate_yaml('shear', "MCMC1", "lsst_y1.dataset")