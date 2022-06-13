def load_to_WorkingRaster(filename, mask=None):
    # -*- coding: utf-8 -*-
    """
    Created on Mon Jan 31 11:29:27 2022
    
    @author: benevans
    
    Loads georeferenced rasters from file using Rasterio and returns an
    instance of class WorkingRaster

    Parameters
    ----------
    filename : String denoting location of file to read

    Returns
    -------
    raster : Instance of class WorkingRaster

    """
    import rasterio, rasterio.mask
    import numpy as np
    from DP_Utils import WorkingRaster
    
    with rasterio.open(filename) as src:
        profile = src.profile#save profile to apply geocoding to output raster  
        
        if mask is not None:
            # by setting crop=true, limits the resulting raster to the extent
            #of features in shapefile
            out_img, out_transform = rasterio.mask.mask(src, mask, crop=True)
            for n in range(out_img.shape[0]):
                band=out_img[n, :, :]
                if n==0:
                    bands=band
                else:
                    bands=np.dstack((bands, band))
            
            raster=WorkingRaster(bands)
            #raster=WorkingRaster(out_img[0,:,:])
            #raster=WorkingRaster(np.reshape(out_img, [out_img.shape[1], out_img.shape[2], out_img.shape[0]]))

            #update profile metadata
            profile['width']=raster.data.shape[1]
            profile['height']=raster.data.shape[0]
            profile['transform']=out_transform
            
        else:
            count=src.count
            for b in range(count):
                src_band = src.read(b+1)#band indexing starts at 1
                if b==0:
                    stack=src_band
                else:
                    stack=np.stack([stack, src_band], 2)
            raster=WorkingRaster(stack)
                
    
    raster.profile=profile
    raster.count=src.count
    raster.source=filename
    
    return raster

def update_transform (target, reference):
    '''
    

    Parameters
    ----------
    target : Str
        Path to georeferenced raster that may need transform metadata updating.
    reference : Str
        Path to georeferenced raster to use as source for transform data. 

    Returns
    -------
    None.
    
    Transforms of the validation raster and the predictions don't match due to 
    precision differences (lower precision for validation raster).
    This can lead to the cropping resulting in different size arrrays. 
    Before processing update the validation transform to match that of one of 
    the run outputs to avoid this problem

    '''
    import rasterio
    
    #open reference file and get transform
    with rasterio.open(reference) as src_ref:
        trans=src_ref.transform
    with rasterio.open(target, 'r+') as src_tar:
        trans2=src_tar.transform
        if trans!=trans2:# if transforms don't already match
            src_tar.transform=trans
            

def precision_recall_curve(y_true, pred_scores, thresholds, plot=False):
    import sklearn.metrics
    import matplotlib.pyplot as plt
    
    precisions = []
    recalls = []
    
    for threshold in thresholds:
        print (threshold)
        y_pred = [1 if score >= threshold else 0 for score in pred_scores]

        precision = sklearn.metrics.precision_score(y_true=y_true, y_pred=y_pred, pos_label=1)
        recall = sklearn.metrics.recall_score(y_true=y_true, y_pred=y_pred, pos_label=1)
        
        precisions.append(precision)
        recalls.append(recall)
        
    if plot == True:
        plt.plot(recalls, precisions, linewidth=4, color="red")
        plt.xlabel("Recall", fontsize=12, fontweight='bold')
        plt.ylabel("Precision", fontsize=12, fontweight='bold')
        plt.title("Precision-Recall Curve", fontsize=15, fontweight="bold")
        plt.show()

    return precisions, recalls

def min_max_scale(X):
    import numpy as np
    X2 = (X-np.amin(X))/(np.amax(X)-np.amin(X))
    return X2

class WorkingRaster:
    # -*- coding: utf-8 -*-
    """
    Created on Mon Jan 31 11:25:22 2022
    
    Class WorkingRaster for use with georeferenced SAR images within the recursive 
    Dirichlet Process clustering algorithm for iceberg detection
    
    @author: benevans
    """

    ##Attributes
    def __init__(self, data):
        self.data=data
    
    def source(self, source):
        self.source=source
            
    def profile(self, profile):
        self.profile=profile
        
    def count(self, count):
        self.count=count

    ##Methods
    def threshold_at(self, thresh, under=0, equal_or_over=1):
        tmp=self.data.copy()
        tmp[self.data < thresh] = under
        tmp[self.data >= thresh] = equal_or_over
        self.data=tmp

    def show(self, **title):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(18,12))
        plt.imshow(self.data)
        if title: 
            plt.title(str(title["title"]))
        plt.show()
        
    def copy(self):
        import copy
        copy_instance=copy.deepcopy(self)
        return copy_instance
    
    def quick_save(self, filename):
        import rasterio
        #check datatypes match profile in case data has been updated
        self.profile['dtype']=str(self.data.dtype)
        with rasterio.open(filename, 'w', **self.profile) as dst:
            dst.write(self.data, self.profile['count'])



